from bs4 import BeautifulSoup
from typing import Dict, Any

def analyse_principle1_perceivable(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    WCAG Principle 1: Perceivable analysis using BeautifulSoup.
    Analyses based on the actual WCAG 2.2 guidelines from principles.md
    Returns a dictionary: {'grade': 'A'|'AA'|'AAA'|'Not WCAG compliant', 'issues': [dict], 'score': int}
    """
    issues = []
    components = []
    
    try:
        # GUIDELINE 1.1: TEXT ALTERNATIVES
        # Success Criterion 1.1.1: Non-text Content (Level A)
        
        # Images with alt text
        imgs = soup.find_all("img")
        total_imgs = len(imgs)
        imgs_with_alt = 0
        decorative_imgs = 0
        
        for img in imgs:
            alt = img.get("alt")
            if alt is not None:
                imgs_with_alt += 1
                if alt == "":  # Decorative image (empty alt)
                    decorative_imgs += 1
        
        if total_imgs > 0:
            alt_score = imgs_with_alt / total_imgs
            components.append(("1.1.1 Images with Alt Text", alt_score, 1,
                [{"component": "1.1.1 Non-text Content", "passed": imgs_with_alt, "total": total_imgs,
                "message": f"{imgs_with_alt}/{total_imgs} images have alt attributes ({decorative_imgs} decorative). WCAG 1.1.1 Level A"}]))
        else:
            components.append(("1.1.1 Images with Alt Text", 1, 1,
                [{"component": "1.1.1 Non-text Content", "passed": 1, "total": 1,
                "message": "No images found. WCAG 1.1.1 Level A compliance: N/A"}]))
        
        # Form controls with labels/names
        form_controls = soup.find_all(["input", "select", "textarea", "button"])
        form_controls = [ctrl for ctrl in form_controls if ctrl.get("type") != "hidden"]
        labelled_controls = 0
        
        for ctrl in form_controls:
            has_label = False
            ctrl_id = ctrl.get("id")
            aria_label = ctrl.get("aria-label")
            aria_labelledby = ctrl.get("aria-labelledby")
            title = ctrl.get("title")
            
            # Check for associated label
            if ctrl_id:
                label = soup.find("label", {"for": ctrl_id})
                if label:
                    has_label = True
            
            # Check for aria-label, aria-labelledby, or title
            if not has_label and (aria_label or aria_labelledby or title):
                has_label = True
            
            # Button with text content
            if not has_label and ctrl.name == "button" and ctrl.get_text(strip=True):
                has_label = True
            
            if has_label:
                labelled_controls += 1
        
        if len(form_controls) > 0:
            controls_score = labelled_controls / len(form_controls)
            components.append(("1.1.1 Form Controls Named", controls_score, 1,
                [{"component": "1.1.1 Non-text Content (Controls)", "passed": labelled_controls, "total": len(form_controls),
                "message": f"{labelled_controls}/{len(form_controls)} form controls have accessible names. WCAG 1.1.1 Level A"}]))
        else:
            components.append(("1.1.1 Form Controls Named", 1, 1,
                [{"component": "1.1.1 Non-text Content (Controls)", "passed": 1, "total": 1,
                "message": "No form controls found. WCAG 1.1.1 Level A compliance: N/A"}]))
        
        # GUIDELINE 1.2: TIME-BASED MEDIA
        # Success Criterion 1.2.1: Audio-only and Video-only (Level A)
        # Success Criterion 1.2.2: Captions (Level A)
        
        media_elements = soup.find_all(["video", "audio"])
        compliant_media = 0
        
        for media in media_elements:
            has_alternative = False
            
            # Check for track elements (captions/subtitles)
            tracks = media.find_all("track")
            if tracks:
                has_alternative = True
            
            # Check for transcript links nearby
            parent = media.parent
            if parent:
                transcript_links = parent.find_all("a", string=lambda text: text and any(word in text.lower() for word in ["transcript", "caption", "subtitle"]))
                if transcript_links:
                    has_alternative = True
            
            if has_alternative:
                compliant_media += 1
        
        if len(media_elements) > 0:
            media_score = compliant_media / len(media_elements)
            components.append(("1.2.1/1.2.2 Media Alternatives", media_score, 1,
                [{"component": "1.2.1-1.2.2 Time-based Media", "passed": compliant_media, "total": len(media_elements),
                "message": f"{compliant_media}/{len(media_elements)} media elements have alternatives (captions/transcripts). WCAG 1.2.1-1.2.2 Level A"}]))
        else:
            components.append(("1.2.1/1.2.2 Media Alternatives", 1, 1,
                [{"component": "1.2.1-1.2.2 Time-based Media", "passed": 1, "total": 1,
                "message": "No media elements found. WCAG 1.2.1-1.2.2 Level A compliance: N/A"}]))
        
        # GUIDELINE 1.3: ADAPTABLE
        # Success Criterion 1.3.1: Info and Relationships (Level A)
        
        # Proper heading structure
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        h1_tags = soup.find_all("h1")
        
        heading_issues = []
        heading_score = 1.0
        
        # Check for exactly one H1
        if len(h1_tags) != 1:
            heading_issues.append(f"Found {len(h1_tags)} H1 tags, should be exactly 1")
            heading_score -= 0.3
        
        # Check heading hierarchy
        if len(headings) > 0:
            last_level = 0
            for heading in headings:
                level = int(heading.name[1])
                if level > last_level + 1:
                    heading_issues.append(f"Heading hierarchy skips levels (found {heading.name} after h{last_level})")
                    heading_score -= 0.3
                    break
                last_level = level
        
        heading_score = max(0, heading_score)
        components.append(("1.3.1 Heading Structure", heading_score, 1,
            [{"component": "1.3.1 Info and Relationships (Headings)", "passed": heading_score, "total": 1,
            "message": f"Heading structure analysis: {'; '.join(heading_issues) if heading_issues else 'Proper heading hierarchy'}. WCAG 1.3.1 Level A"}]))
        
        # Lists structure
        lists = soup.find_all(["ul", "ol", "dl"])
        proper_lists = 0
        
        for lst in lists:
            if lst.name in ["ul", "ol"]:
                # Check if contains li elements
                lis = lst.find_all("li", recursive=False)
                if lis:
                    proper_lists += 1
            elif lst.name == "dl":
                # Check if contains dt/dd elements
                dts = lst.find_all("dt", recursive=False)
                dds = lst.find_all("dd", recursive=False)
                if dts and dds:
                    proper_lists += 1
        
        if len(lists) > 0:
            lists_score = proper_lists / len(lists)
            components.append(("1.3.1 List Structure", lists_score, 1,
                [{"component": "1.3.1 Info and Relationships (Lists)", "passed": proper_lists, "total": len(lists),
                "message": f"{proper_lists}/{len(lists)} lists are properly structured. WCAG 1.3.1 Level A"}]))
        else:
            components.append(("1.3.1 List Structure", 1, 1,
                [{"component": "1.3.1 Info and Relationships (Lists)", "passed": 1, "total": 1,
                "message": "No lists found. WCAG 1.3.1 Level A compliance: N/A"}]))
        
        # Tables with headers
        tables = soup.find_all("table")
        accessible_tables = 0
        
        for table in tables:
            has_headers = False
            
            # Check for th elements
            ths = table.find_all("th")
            if ths:
                has_headers = True
            
            # Check for thead
            thead = table.find("thead")
            if thead:
                has_headers = True
            
            # Check for caption
            caption = table.find("caption")
            if caption:
                has_headers = True
            
            if has_headers:
                accessible_tables += 1
        
        if len(tables) > 0:
            tables_score = accessible_tables / len(tables)
            components.append(("1.3.1 Table Headers", tables_score, 1,
                [{"component": "1.3.1 Info and Relationships (Tables)", "passed": accessible_tables, "total": len(tables),
                "message": f"{accessible_tables}/{len(tables)} tables have proper headers/structure. WCAG 1.3.1 Level A"}]))
        else:
            components.append(("1.3.1 Table Headers", 1, 1,
                [{"component": "1.3.1 Info and Relationships (Tables)", "passed": 1, "total": 1,
                "message": "No tables found. WCAG 1.3.1 Level A compliance: N/A"}]))
        
        # Success Criterion 1.3.3: Sensory Characteristics (Level A)
        # Check for instructions that rely solely on sensory characteristics
        sensory_words = ["click here", "red button", "green link", "left side", "right side", "above", "below", "round button", "square icon"]
        sensory_violations = 0
        
        all_text = soup.get_text().lower()
        for word in sensory_words:
            if word in all_text:
                sensory_violations += 1
        
        sensory_score = max(0, 1 - (sensory_violations * 0.1))
        components.append(("1.3.3 Sensory Characteristics", sensory_score, 1,
            [{"component": "1.3.3 Sensory Characteristics", "passed": sensory_score, "total": 1,
            "message": f"Found {sensory_violations} potential sensory-only instructions. WCAG 1.3.3 Level A"}]))
        
        # GUIDELINE 1.4: DISTINGUISHABLE
        # Success Criterion 1.4.1: Use of Colour (Level A)
        
        # Check for colour-only information (basic detection)
        colour_only_indicators = soup.find_all(attrs={"style": lambda x: x and any(colour in x.lower() for colour in ["color:", "background-color:"])})
        links_with_colour_only = soup.find_all("a", attrs={"style": lambda x: x and "color:" in x.lower() and "text-decoration: none" in x.lower()})
        
        colour_score = 1.0
        if len(links_with_colour_only) > 0:
            colour_score -= 0.3
        
        colour_score = max(0, colour_score)
        components.append(("1.4.1 Use of Colour", colour_score, 1,
            [{"component": "1.4.1 Use of Colour", "passed": colour_score, "total": 1,
            "message": f"Colour usage analysis: {len(links_with_colour_only)} links may rely on colour alone. WCAG 1.4.1 Level A"}]))
        
        # Success Criterion 1.4.2: Audio Control (Level A)
        audio_autoplay = soup.find_all(["audio", "video"], attrs={"autoplay": True})
        audio_score = 1.0 if len(audio_autoplay) == 0 else 0.0
        
        components.append(("1.4.2 Audio Control", audio_score, 1,
            [{"component": "1.4.2 Audio Control", "passed": 1 if audio_score == 1.0 else 0, "total": 1,
            "message": f"Found {len(audio_autoplay)} autoplay media elements. WCAG 1.4.2 Level A"}]))
        
        # Language declaration
        html_tag = soup.find("html")
        has_lang = html_tag and html_tag.get("lang")
        lang_score = 1.0 if has_lang else 0.0
        
        components.append(("Language Declaration", lang_score, 1,
            [{"component": "Language Declaration", "passed": 1 if has_lang else 0, "total": 1,
            "message": f"HTML lang attribute: {'Present' if has_lang else 'Missing'}. WCAG 3.1.1 Level A"}]))
        
        # Page title
        title_tag = soup.find("title")
        has_title = title_tag and title_tag.get_text(strip=True)
        title_score = 1.0 if has_title else 0.0
        
        components.append(("Page Title", title_score, 1,
            [{"component": "Page Title", "passed": 1 if has_title else 0, "total": 1,
            "message": f"Page title: {'Present' if has_title else 'Missing'}. WCAG 2.4.2 Level A"}]))
        
    except Exception as e:
        return {
            "grade": "Error",
            "issues": [{"component": "WCAG Principle 1 Analysis", "passed": 0, "total": 1, 
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
