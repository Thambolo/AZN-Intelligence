from bs4 import BeautifulSoup
from typing import Dict, Any

def analyse_principle3_understandable(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Analyse website for WCAG 2.2 Principle 3: Understandable
    Information and the operation of user interface must be understandable.
    
    NOTE: This analysis has limited accuracy using HTML-only parsing.
    Many understandability criteria require user testing, content analysis,
    and interaction testing that cannot be performed statically.
    """
    try:
        issues = []
        total_score = 0
        max_score = 17  # 17 success criteria for Principle 3
        
        # GUIDELINE 3.1: READABLE
        # Success Criterion 3.1.1: Language of Page (Level A)
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            total_score += 1
            issues.append({
                "component": "Language of Page",
                "passed": 1,
                "total": 1,
                "message": f"Page language declared: {html_tag.get('lang')}"
            })
        else:
            issues.append({
                "component": "Language of Page",
                "passed": 0,
                "total": 1,
                "message": "Missing lang attribute on <html> element"
            })
        
        # Success Criterion 3.1.2: Language of Parts (Level AA)
        lang_elements = soup.find_all(attrs={"lang": True})
        if lang_elements:
            total_score += 1
            issues.append({
                "component": "Language of Parts",
                "passed": 1,
                "total": 1,
                "message": f"Found {len(lang_elements)} elements with language declarations"
            })
        else:
            issues.append({
                "component": "Language of Parts",
                "passed": 0,
                "total": 1,
                "message": "No language declarations found for content parts"
            })
        
        # Success Criterion 3.1.3: Unusual Words (Level AAA)
        # Check for mechanisms to identify definitions of unusual words, idioms, and jargon
        # Look for glossaries, definition lists, tooltips, or other definition mechanisms
        definition_mechanisms = 0
        
        # Check for definition lists
        dl_elements = soup.find_all("dl")
        definition_mechanisms += len(dl_elements)
        
        # Check for elements with title attributes (tooltips)
        title_elements = soup.find_all(attrs={"title": lambda x: x and len(x) > 10})  # Substantial tooltips
        definition_mechanisms += len(title_elements)
        
        # Check for glossary or definition links
        definition_links = soup.find_all("a", href=lambda x: x and any(word in x.lower() for word in ["glossary", "definition", "define"]))
        definition_mechanisms += len(definition_links)
        
        # Check for definition classes or data attributes
        def_classes = soup.find_all(class_=lambda x: x and any(word in str(x).lower() for word in ["definition", "tooltip", "glossary"]))
        definition_mechanisms += len(def_classes)
        
        unusual_words_score = 1 if definition_mechanisms > 0 else 0
        total_score += unusual_words_score
        issues.append({
            "component": "Unusual Words",
            "passed": unusual_words_score,
            "total": 1,
            "message": f"Found {definition_mechanisms} definition mechanisms (glossaries, tooltips, definition lists)"
        })
        
        # Success Criterion 3.1.4: Abbreviations (Level AAA)
        # Check for abbreviations and acronyms with explanations
        abbr_elements = soup.find_all(["abbr", "acronym"])
        abbr_with_title = len([elem for elem in abbr_elements if elem.get("title")])
        abbr_score = 1 if abbr_with_title == len(abbr_elements) and len(abbr_elements) > 0 else (1 if len(abbr_elements) == 0 else 0)
        total_score += abbr_score
        issues.append({
            "component": "Abbreviations",
            "passed": abbr_score,
            "total": 1,
            "message": f"{abbr_with_title}/{len(abbr_elements)} abbreviations have explanations" if len(abbr_elements) > 0 else "No abbreviations found"
        })
        
        # Success Criterion 3.1.5: Reading Level (Level AAA)
        # Basic text complexity analysis
        text_content = soup.get_text()
        words = text_content.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        reading_level_score = 1 if avg_word_length < 6 else 0  # Simple heuristic
        total_score += reading_level_score
        issues.append({
            "component": "Reading Level",
            "passed": reading_level_score,
            "total": 1,
            "message": f"Average word length: {avg_word_length:.1f} characters"
        })
        
        # Success Criterion 3.1.6: Pronunciation (Level AAA)
        # Check for pronunciation guides (ruby tags, phonetic notations)
        ruby_elements = soup.find_all("ruby")
        pronunciation_score = 1 if len(ruby_elements) > 0 else 0
        total_score += pronunciation_score
        issues.append({
            "component": "Pronunciation",
            "passed": pronunciation_score,
            "total": 1,
            "message": f"Found {len(ruby_elements)} pronunciation guide elements"
        })
        
        # GUIDELINE 3.2: PREDICTABLE
        # Success Criterion 3.2.1: On Focus (Level A)
        # Check for elements that might cause context changes on focus
        focus_elements = soup.find_all(["input", "select", "button"])
        focus_issues = 0
        for elem in focus_elements:
            # Check for automatic form submission or navigation on focus
            if elem.get("onfocus") and ("submit" in elem.get("onfocus").lower() or "location" in elem.get("onfocus").lower()):
                focus_issues += 1
        
        focus_score = 1 if focus_issues == 0 else 0
        total_score += focus_score
        issues.append({
            "component": "On Focus",
            "passed": focus_score,
            "total": 1,
            "message": f"Found {focus_issues} potential focus-triggered context changes"
        })
        
        # Success Criterion 3.2.2: On Input (Level A)
        # Check for form elements that cause context changes
        input_elements = soup.find_all(["input", "select"])
        input_issues = 0
        for elem in input_elements:
            # Check for automatic submission on input change
            onchange = elem.get("onchange", "")
            if "submit" in onchange.lower() or "location" in onchange.lower():
                input_issues += 1
        
        input_score = 1 if input_issues == 0 else 0
        total_score += input_score
        issues.append({
            "component": "On Input",
            "passed": input_score,
            "total": 1,
            "message": f"Found {input_issues} potential input-triggered context changes"
        })
        
        # Success Criterion 3.2.3: Consistent Navigation (Level AA)
        # Check for consistent navigation patterns
        nav_elements = soup.find_all("nav")
        navigation_score = 1 if len(nav_elements) > 0 else 0
        total_score += navigation_score
        issues.append({
            "component": "Consistent Navigation",
            "passed": navigation_score,
            "total": 1,
            "message": f"Found {len(nav_elements)} navigation landmarks"
        })
        
        # Success Criterion 3.2.4: Consistent Identification (Level AA)
        # Check for consistent labelling of similar components
        buttons = soup.find_all("button")
        links = soup.find_all("a")
        consistent_id_score = 1 if len(buttons) > 0 or len(links) > 0 else 0
        total_score += consistent_id_score
        issues.append({
            "component": "Consistent Identification",
            "passed": consistent_id_score,
            "total": 1,
            "message": f"Found {len(buttons)} buttons and {len(links)} links for consistency analysis"
        })
        
        # Success Criterion 3.2.5: Change on Request (Level AAA)
        # Check that context changes are initiated by user request
        auto_refresh = soup.find("meta", {"http-equiv": "refresh"})
        auto_redirect = soup.find("meta", {"http-equiv": "refresh", "content": lambda x: x and "url=" in x.lower()})
        change_request_score = 1 if not auto_refresh and not auto_redirect else 0
        total_score += change_request_score
        issues.append({
            "component": "Change on Request",
            "passed": change_request_score,
            "total": 1,
            "message": "No automatic redirects or refreshes found" if change_request_score else "Automatic page changes detected"
        })
        
        # GUIDELINE 3.3: INPUT ASSISTANCE
        # Success Criterion 3.3.1: Error Identification (Level A)
        # Check for error identification mechanisms
        error_elements = soup.find_all(class_=lambda x: x and "error" in x.lower())
        error_messages = soup.find_all(attrs={"role": "alert"})
        error_id_score = 1 if len(error_elements) > 0 or len(error_messages) > 0 else 0
        total_score += error_id_score
        issues.append({
            "component": "Error Identification",
            "passed": error_id_score,
            "total": 1,
            "message": f"Found {len(error_elements + error_messages)} error identification elements"
        })
        
        # Success Criterion 3.3.2: Labels or Instructions (Level A)
        form_elements = soup.find_all(["input", "select", "textarea"])
        labelled_elements = 0
        for elem in form_elements:
            elem_id = elem.get("id")
            elem_name = elem.get("name")
            # Check for associated label
            if elem_id and soup.find("label", {"for": elem_id}):
                labelled_elements += 1
            elif elem.find_parent("label"):
                labelled_elements += 1
            elif elem.get("aria-label") or elem.get("aria-labelledby"):
                labelled_elements += 1
            elif elem.get("placeholder") and elem.get("type") in ["text", "email", "password"]:
                labelled_elements += 1
        
        labels_score = 1 if labelled_elements == len(form_elements) and len(form_elements) > 0 else (1 if len(form_elements) == 0 else 0)
        total_score += labels_score
        issues.append({
            "component": "Labels or Instructions",
            "passed": labels_score,
            "total": 1,
            "message": f"{labelled_elements}/{len(form_elements)} form elements have labels or instructions"
        })
        
        # Success Criterion 3.3.3: Error Suggestion (Level AA)
        # Check for error correction suggestions
        error_suggestion_score = error_id_score  # If errors are identified, assume suggestions are provided
        total_score += error_suggestion_score
        issues.append({
            "component": "Error Suggestion",
            "passed": error_suggestion_score,
            "total": 1,
            "message": "Error suggestion mechanisms available" if error_suggestion_score else "No error suggestion mechanisms found"
        })
        
        # Success Criterion 3.3.4: Error Prevention (Legal, Financial, Data) (Level AA)
        # Check for confirmation mechanisms
        confirmation_elements = soup.find_all(text=lambda x: x and ("confirm" in x.lower() or "verify" in x.lower()))
        prevention_score = 1 if len(confirmation_elements) > 0 else 0
        total_score += prevention_score
        issues.append({
            "component": "Error Prevention",
            "passed": prevention_score,
            "total": 1,
            "message": f"Found {len(confirmation_elements)} confirmation/verification elements"
        })
        
        # Success Criterion 3.3.5: Help (Level AAA)
        help_elements = soup.find_all(text=lambda x: x and "help" in x.lower())
        help_links = soup.find_all("a", href=lambda x: x and "help" in x.lower())
        help_score = 1 if len(help_elements) > 0 or len(help_links) > 0 else 0
        total_score += help_score
        issues.append({
            "component": "Help",
            "passed": help_score,
            "total": 1,
            "message": f"Found {len(help_elements + help_links)} help elements"
        })
        
        # Success Criterion 3.3.6: Error Prevention (All) (Level AAA)
        # Enhanced error prevention for all submissions
        submit_buttons = soup.find_all(["input", "button"], type="submit")
        enhanced_prevention_score = 1 if len(submit_buttons) > 0 and len(confirmation_elements) > 0 else 0
        total_score += enhanced_prevention_score
        issues.append({
            "component": "Error Prevention (All)",
            "passed": enhanced_prevention_score,
            "total": 1,
            "message": "Enhanced error prevention mechanisms found" if enhanced_prevention_score else "No enhanced error prevention found"
        })
        
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
            "principle": "Principle 3: Understandable"
        }
        
    except Exception as e:
        return {
            "grade": "Error",
            "issues": [{"component": "WCAG Principle 3 Analysis", "passed": 0, "total": 1,
                       "message": f"Principle 3 analysis failed: {str(e)}"}],
            "score": 0,
            "error": str(e)
        }
