from bs4 import BeautifulSoup
from typing import Dict, Any

def analyse_principle2_operable(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    WCAG Principle 2: Operable analysis using BeautifulSoup.
    Analyses based on the actual WCAG 2.2 guidelines from principles.md
    Returns a dictionary: {'grade': 'A'|'AA'|'AAA'|'Not WCAG compliant', 'issues': [dict], 'score': int}
    """
    issues = []
    components = []
    
    try:
        # GUIDELINE 2.1: KEYBOARD ACCESSIBLE
        # Success Criterion 2.1.1: Keyboard (Level A)
        # Check for keyboard accessible elements
        
        # Interactive elements that should be keyboard accessible
        interactive_elements = soup.find_all(["a", "button", "input", "select", "textarea"])
        keyboard_accessible = 0
        
        for element in interactive_elements:
            # Check if element has proper tabindex (not negative) or is naturally focusable
            tabindex = element.get("tabindex")
            if tabindex is None or (tabindex and int(tabindex) >= 0):
                keyboard_accessible += 1
            # Elements with onclick but no keyboard equivalent
            elif element.get("onclick") and not element.get("onkeydown") and not element.get("onkeypress"):
                # This is a potential keyboard accessibility issue
                pass
        
        if len(interactive_elements) > 0:
            keyboard_score = keyboard_accessible / len(interactive_elements)
            components.append(("2.1.1 Keyboard Accessible", keyboard_score, 1,
                [{"component": "2.1.1 Keyboard", "passed": keyboard_accessible, "total": len(interactive_elements),
                "message": f"{keyboard_accessible}/{len(interactive_elements)} interactive elements are keyboard accessible. WCAG 2.1.1 Level A"}]))
        else:
            components.append(("2.1.1 Keyboard Accessible", 1, 1,
                [{"component": "2.1.1 Keyboard", "passed": 1, "total": 1,
                "message": "No interactive elements found. WCAG 2.1.1 Level A compliance: N/A"}]))
        
        # Success Criterion 2.1.2: No Keyboard Trap (Level A)
        # Check for elements with tabindex that might cause keyboard traps
        trap_elements = soup.find_all(attrs={"tabindex": lambda x: x and int(x) < -1}) if soup.find_all(attrs={"tabindex": True}) else []
        no_trap_score = 1.0 if len(trap_elements) == 0 else 0.0
        
        components.append(("2.1.2 No Keyboard Trap", no_trap_score, 1,
            [{"component": "2.1.2 No Keyboard Trap", "passed": 1 if no_trap_score == 1.0 else 0, "total": 1,
            "message": f"Found {len(trap_elements)} potential keyboard traps. WCAG 2.1.2 Level A"}]))
        
        # GUIDELINE 2.2: ENOUGH TIME
        # Success Criterion 2.2.1: Timing Adjustable (Level A)
        # Check for refresh/redirect meta tags
        
        refresh_meta = soup.find_all("meta", attrs={"http-equiv": lambda x: x and x.lower() == "refresh"})
        timing_issues = 0
        
        for meta in refresh_meta:
            content = meta.get("content", "")
            if content and ";" in content:
                # Check if refresh time is very short (less than 20 hours = 72000 seconds)
                try:
                    seconds = int(content.split(";")[0])
                    if seconds < 72000:  # Less than 20 hours
                        timing_issues += 1
                except (ValueError, IndexError):
                    timing_issues += 1
        
        timing_score = 1.0 if timing_issues == 0 else 0.0
        components.append(("2.2.1 Timing Adjustable", timing_score, 1,
            [{"component": "2.2.1 Timing Adjustable", "passed": 1 if timing_score == 1.0 else 0, "total": 1,
            "message": f"Found {timing_issues} potential timing issues (auto-refresh/redirect). WCAG 2.2.1 Level A"}]))
        
        # Success Criterion 2.2.2: Pause, Stop, Hide (Level A)
        # Check for auto-playing media and moving content
        
        autoplay_media = soup.find_all(["video", "audio"], attrs={"autoplay": True})
        moving_elements = soup.find_all(attrs={"style": lambda x: x and any(anim in x.lower() for anim in ["animation", "transition", "@keyframes"])})
        
        pause_stop_issues = len(autoplay_media)
        if len(moving_elements) > 5:  # Threshold for too many animated elements
            pause_stop_issues += 1
        
        pause_score = 1.0 if pause_stop_issues == 0 else max(0, 1 - (pause_stop_issues * 0.3))
        components.append(("2.2.2 Pause, Stop, Hide", pause_score, 1,
            [{"component": "2.2.2 Pause, Stop, Hide", "passed": pause_score, "total": 1,
            "message": f"Found {len(autoplay_media)} autoplay media elements and {len(moving_elements)} animated elements. WCAG 2.2.2 Level A"}]))
        
        # GUIDELINE 2.3: SEIZURES AND PHYSICAL REACTIONS
        # Success Criterion 2.3.1: Three Flashes or Below Threshold (Level A)
        
        # Check for rapidly flashing content (basic detection)
        flash_elements = soup.find_all(attrs={"style": lambda x: x and any(flash in x.lower() for flash in ["blink", "flash", "strobe"])})
        flash_classes = soup.find_all(attrs={"class": lambda x: x and any(flash in str(x).lower() for flash in ["blink", "flash", "strobe"])})
        
        flash_count = len(flash_elements) + len(flash_classes)
        flash_score = 1.0 if flash_count == 0 else 0.0
        
        components.append(("2.3.1 Three Flashes", flash_score, 1,
            [{"component": "2.3.1 Three Flashes or Below Threshold", "passed": 1 if flash_score == 1.0 else 0, "total": 1,
            "message": f"Found {flash_count} potentially flashing elements. WCAG 2.3.1 Level A"}]))
        
        # GUIDELINE 2.4: NAVIGABLE
        # Success Criterion 2.4.1: Bypass Blocks (Level A)
        
        # Check for skip links or landmark navigation
        skip_links = soup.find_all("a", href=lambda x: x and x.startswith("#"))
        landmarks = soup.find_all(["nav", "main", "header", "footer"]) + soup.find_all(attrs={"role": lambda x: x and x in ["navigation", "main", "banner", "contentinfo"]})
        
        bypass_mechanisms = len(skip_links) + len(landmarks)
        bypass_score = 1.0 if bypass_mechanisms > 0 else 0.0
        
        components.append(("2.4.1 Bypass Blocks", bypass_score, 1,
            [{"component": "2.4.1 Bypass Blocks", "passed": 1 if bypass_score == 1.0 else 0, "total": 1,
            "message": f"Found {len(skip_links)} skip links and {len(landmarks)} landmark elements. WCAG 2.4.1 Level A"}]))
        
        # Success Criterion 2.4.2: Page Titled (Level A) - Already covered in Principle 1
        title_tag = soup.find("title")
        has_title = title_tag and title_tag.get_text(strip=True)
        title_score = 1.0 if has_title else 0.0
        
        components.append(("2.4.2 Page Titled", title_score, 1,
            [{"component": "2.4.2 Page Titled", "passed": 1 if has_title else 0, "total": 1,
            "message": f"Page title: {'Present' if has_title else 'Missing'}. WCAG 2.4.2 Level A"}]))
        
        # Success Criterion 2.4.3: Focus Order (Level A)
        # Check for logical tabindex values
        
        tabindex_elements = soup.find_all(attrs={"tabindex": True})
        logical_tabindex = 0
        total_tabindex = len(tabindex_elements)
        
        for element in tabindex_elements:
            tabindex = element.get("tabindex")
            try:
                tab_val = int(tabindex)
                if tab_val >= 0:  # Positive or zero tabindex is generally acceptable
                    logical_tabindex += 1
            except (ValueError, TypeError):
                pass
        
        if total_tabindex > 0:
            focus_order_score = logical_tabindex / total_tabindex
        else:
            focus_order_score = 1.0  # No explicit tabindex means natural order
        
        components.append(("2.4.3 Focus Order", focus_order_score, 1,
            [{"component": "2.4.3 Focus Order", "passed": logical_tabindex, "total": max(1, total_tabindex),
            "message": f"{logical_tabindex}/{max(1, total_tabindex)} tabindex values are logical. WCAG 2.4.3 Level A"}]))
        
        # Success Criterion 2.4.4: Link Purpose (In Context) (Level A)
        
        links = soup.find_all("a", href=True)
        descriptive_links = 0
        vague_link_text = ["click here", "read more", "more", "link", "here", "this"]
        
        for link in links:
            link_text = link.get_text(strip=True).lower()
            aria_label = link.get("aria-label", "").strip()
            title = link.get("title", "").strip()
            
            # Check if link has descriptive text
            if link_text and link_text not in vague_link_text:
                descriptive_links += 1
            elif aria_label or title:  # Has alternative description
                descriptive_links += 1
            elif len(link_text) > 4:  # Longer text is generally more descriptive
                descriptive_links += 1
        
        if len(links) > 0:
            link_purpose_score = descriptive_links / len(links)
        else:
            link_purpose_score = 1.0
        
        components.append(("2.4.4 Link Purpose", link_purpose_score, 1,
            [{"component": "2.4.4 Link Purpose (In Context)", "passed": descriptive_links, "total": max(1, len(links)),
            "message": f"{descriptive_links}/{max(1, len(links))} links have descriptive text. WCAG 2.4.4 Level A"}]))
        
        # Success Criterion 2.4.6: Headings and Labels (Level AA)
        
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        descriptive_headings = 0
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if len(heading_text) > 2:  # Basic check for non-empty meaningful headings
                descriptive_headings += 1
        
        labels = soup.find_all("label")
        descriptive_labels = 0
        
        for label in labels:
            label_text = label.get_text(strip=True)
            if len(label_text) > 1:  # Basic check for meaningful labels
                descriptive_labels += 1
        
        total_heading_label = len(headings) + len(labels)
        total_descriptive = descriptive_headings + descriptive_labels
        
        if total_heading_label > 0:
            heading_label_score = total_descriptive / total_heading_label
        else:
            heading_label_score = 1.0
        
        components.append(("2.4.6 Headings and Labels", heading_label_score, 1,
            [{"component": "2.4.6 Headings and Labels", "passed": total_descriptive, "total": max(1, total_heading_label),
            "message": f"{total_descriptive}/{max(1, total_heading_label)} headings and labels are descriptive. WCAG 2.4.6 Level AA"}]))
        
        # GUIDELINE 2.5: INPUT MODALITIES
        # Success Criterion 2.5.3: Label in Name (Level A)
        
        labelled_inputs = soup.find_all(["input", "button"], attrs={"aria-label": True})
        labelled_inputs.extend(soup.find_all(["input", "button"], attrs={"title": True}))
        
        consistent_labels = 0
        for element in labelled_inputs:
            visible_text = element.get_text(strip=True).lower()
            aria_label = element.get("aria-label", "").lower()
            title = element.get("title", "").lower()
            
            # Check if visible text is contained in accessible name
            if visible_text and (visible_text in aria_label or visible_text in title):
                consistent_labels += 1
            elif not visible_text:  # No visible text to conflict
                consistent_labels += 1
        
        if len(labelled_inputs) > 0:
            label_name_score = consistent_labels / len(labelled_inputs)
        else:
            label_name_score = 1.0
        
        components.append(("2.5.3 Label in Name", label_name_score, 1,
            [{"component": "2.5.3 Label in Name", "passed": consistent_labels, "total": max(1, len(labelled_inputs)),
            "message": f"{consistent_labels}/{max(1, len(labelled_inputs))} labelled elements have consistent names. WCAG 2.5.3 Level A"}]))
        
        # Success Criterion 2.5.8: Target Size (Minimum) (Level AA)
        # This is difficult to assess without CSS computation, so we'll do a basic check
        
        clickable_elements = soup.find_all(["button", "a", "input"])
        clickable_elements = [el for el in clickable_elements if el.get("type") not in ["hidden"]]
        
        # Basic heuristic: assume standard sizing is adequate unless inline styles suggest otherwise
        undersized_targets = 0
        for element in clickable_elements:
            style = element.get("style", "")
            if style and any(small in style.lower() for small in ["width:1", "height:1", "font-size:1"]):
                undersized_targets += 1
        
        target_size_score = 1.0 if undersized_targets == 0 else max(0, 1 - (undersized_targets * 0.1))
        
        components.append(("2.5.8 Target Size", target_size_score, 1,
            [{"component": "2.5.8 Target Size (Minimum)", "passed": target_size_score, "total": 1,
            "message": f"Found {undersized_targets} potentially undersized targets. WCAG 2.5.8 Level AA"}]))
        
    except Exception as e:
        return {
            "grade": "Error",
            "issues": [{"component": "WCAG Principle 2 Analysis", "passed": 0, "total": 1, 
                       "message": f"Analysis failed: {str(e)}"}],
            "score": 0,
            "error": str(e)
        }
    
    # Calculate WCAG Compliance Score
    total_components = len(components)
    if total_components == 0:
        score = 0
        grade = "Error"
        issues = [{"component": "General", "message": "No accessibility components analysed.", "passed": 0, "total": 1}]
    else:
        # Each component is equally weighted
        component_scores = []
        for name, passed, total, comp_issues in components:
            if total > 0:
                component_score = passed / total
            else:
                component_score = 1.0
            component_scores.append(component_score)
            issues.extend(comp_issues)
        
        avg_score = sum(component_scores) / total_components
        score = int(round(avg_score * 100))
        
        # WCAG Grade assignment based on compliance level
        if score >= 95:
            grade = "AAA"  # Highest level of accessibility
        elif score >= 85:
            grade = "AA"   # Standard compliance level
        elif score >= 70:
            grade = "A"    # Basic compliance level
        else:
            grade = "Not WCAG compliant"
    
    return {"grade": grade, "issues": issues, "score": score}
