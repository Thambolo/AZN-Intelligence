from bs4 import BeautifulSoup
from typing import Dict, Any

def analyse_principle4_robust(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Analyse website for WCAG 2.2 Principle 4: Robust
    Content must be robust enough that it can be interpreted by a wide variety of user agents, including assistive technologies.
    
    NOTE: This analysis has limited accuracy using HTML-only parsing.
    True robustness testing requires cross-browser testing, assistive technology testing,
    and dynamic interaction testing that cannot be performed with static HTML analysis.
    """
    try:
        issues = []
        total_score = 0
        max_score = 2  # 2 active success criteria for Principle 4 (4.1.1 is obsolete)
        
        # GUIDELINE 4.1: COMPATIBLE
        # Success Criterion 4.1.1: Parsing (Obsolete and removed)
        # Note: This criterion is obsolete and removed in WCAG 2.2, so we skip it
        
        # Success Criterion 4.1.2: Name, Role, Value (Level A)
        # Check for proper naming, roles, and values of UI components
        
        # Form elements with proper labels and roles
        form_elements = soup.find_all(["input", "select", "textarea", "button"])
        properly_named = 0
        
        for elem in form_elements:
            has_name = False
            has_role = True  # Most HTML elements have implicit roles
            
            # Check for accessible name
            elem_id = elem.get("id")
            aria_label = elem.get("aria-label")
            aria_labelledby = elem.get("aria-labelledby")
            title = elem.get("title")
            
            # Associated label
            if elem_id and soup.find("label", {"for": elem_id}):
                has_name = True
            # Parent label
            elif elem.find_parent("label"):
                has_name = True
            # ARIA label
            elif aria_label or aria_labelledby:
                has_name = True
            # Title attribute
            elif title:
                has_name = True
            # Button with text content
            elif elem.name == "button" and elem.get_text(strip=True):
                has_name = True
            # Input with value (for buttons)
            elif elem.name == "input" and elem.get("type") in ["submit", "button", "reset"] and elem.get("value"):
                has_name = True
            
            if has_name:
                properly_named += 1
        
        # Links with proper names
        links = soup.find_all("a", href=True)
        properly_named_links = 0
        
        for link in links:
            link_text = link.get_text(strip=True)
            aria_label = link.get("aria-label")
            aria_labelledby = link.get("aria-labelledby")
            title = link.get("title")
            
            if link_text or aria_label or aria_labelledby or title:
                properly_named_links += 1
        
        total_interactive = len(form_elements) + len(links)
        total_properly_named = properly_named + properly_named_links
        
        if total_interactive > 0:
            name_role_score = total_properly_named / total_interactive
            if name_role_score >= 0.95:
                total_score += 1
            elif name_role_score >= 0.8:
                total_score += 0.8
            elif name_role_score >= 0.6:
                total_score += 0.6
            else:
                total_score += name_role_score
        else:
            total_score += 1  # No interactive elements to evaluate
        
        issues.append({
            "component": "Name, Role, Value",
            "passed": total_properly_named,
            "total": max(1, total_interactive),
            "message": f"{total_properly_named}/{max(1, total_interactive)} interactive elements have proper names and roles"
        })
        
        # Check for ARIA roles and properties
        aria_elements = soup.find_all(attrs={"role": True})
        aria_labels = soup.find_all(attrs={"aria-label": True})
        aria_described = soup.find_all(attrs={"aria-describedby": True})
        aria_states = soup.find_all(attrs=lambda x: x and any(attr.startswith("aria-") for attr in x if isinstance(x, dict)))
        
        aria_usage = len(aria_elements) + len(aria_labels) + len(aria_described)
        aria_score_bonus = min(0.2, aria_usage * 0.02)  # Bonus for ARIA usage, up to 20%
        
        # Success Criterion 4.1.3: Status Messages (Level AA)
        # Check for proper status message implementation
        
        # ARIA live regions
        live_regions = soup.find_all(attrs={"aria-live": True})
        
        # Status/alert roles
        status_roles = soup.find_all(attrs={"role": lambda x: x and x.lower() in ["status", "alert", "log", "marquee", "timer"]})
        
        # Elements with status-related classes
        status_classes = soup.find_all(class_=lambda x: x and any(status in str(x).lower() for status in ["status", "alert", "message", "notification", "toast"]))
        
        # Error message containers
        error_containers = soup.find_all(class_=lambda x: x and "error" in str(x).lower())
        error_roles = soup.find_all(attrs={"role": "alert"})
        
        # Success message containers
        success_containers = soup.find_all(class_=lambda x: x and any(word in str(x).lower() for word in ["success", "confirm", "complete"]))
        
        status_mechanisms = len(live_regions) + len(status_roles) + len(error_roles)
        
        if status_mechanisms > 0:
            total_score += 1
            status_message_score = 1
        elif len(status_classes) > 0 or len(error_containers) > 0 or len(success_containers) > 0:
            total_score += 0.5  # Partial credit for status-related elements without proper ARIA
            status_message_score = 0.5
        else:
            status_message_score = 0
        
        issues.append({
            "component": "Status Messages",
            "passed": status_message_score,
            "total": 1,
            "message": f"Found {status_mechanisms} ARIA live regions/status roles and {len(status_classes)} status-related elements"
        })
        
        # Apply ARIA usage bonus to total score
        total_score = min(max_score, total_score + aria_score_bonus)
        
        # Calculate final grade and score
        percentage_score = (total_score / max_score) * 100
        
        # WCAG Grade assignment based on compliance level
        if percentage_score >= 95:
            grade = "AAA"  # Highest level of accessibility
        elif percentage_score >= 85:
            grade = "AA"   # Standard compliance level
        elif percentage_score >= 70:
            grade = "A"    # Basic compliance level
        else:
            grade = "Not WCAG compliant"
        
        return {
            "grade": grade,
            "issues": issues,
            "score": int(percentage_score),
            "total_criteria": max_score,
            "passed_criteria": total_score,
            "principle": "Principle 4: Robust"
        }
        
    except Exception as e:
        return {
            "grade": "Error",
            "issues": [{"component": "WCAG Principle 4 Analysis", "passed": 0, "total": 1,
                       "message": f"Principle 4 analysis failed: {str(e)}"}],
            "score": 0,
            "error": str(e)
        }
