import re
from typing import Dict, List
from utils.extract_pdf_match import extract_text_from_pdf


def extract_pdf_for_summary(cv_path: str) -> str:
    """
    Search for a PDF file across role folders and extract its content to a long string.

    Args:
        cv_path (str): Path of the PDF file to search for

    Returns:
        str: Extracted text content as a long string, or empty string if file not found/error
    """

    extracted_text = extract_text_from_pdf(cv_path)
    processed_text = _clean_text(extracted_text)

    return processed_text


def _clean_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text.

    Args:
        text (str): Raw extracted text

    Returns:
        str: Cleaned text
    """

    if not text:
        return ""

    # Remove extra line breaks and normalize spacing
    text = re.sub(r'\n\s*\n', '\n', text)

    text = text.strip()
    return text


def extract_pdf_to_regex_string(cv_path: str) -> Dict[str, str]:
    """
    Extract PDF content and convert to structured regex patterns for CV sections.

    Args:
        cv_path (str): Path of the PDF file to process

    Returns:
        Dict[str, str]: Dictionary containing extracted sections and their regex patterns
    """

    # Extract PDF content
    pdf_content = extract_pdf_for_summary(cv_path)

    if not pdf_content:
        return None

    # Extract sections
    cv_sections = _extract_cv_sections(pdf_content)
    return cv_sections


def _extract_cv_sections(text: str) -> Dict[str, str]:
    """
    Extract specific CV sections from text using pattern matching.

    Args:
        text (str): Full CV text content

    Returns:
        Dict[str, str]: Dictionary with extracted sections
    """

    sections = {
        'summary': '',
        'skills': '',
        'experience': '',
        'education': ''
    }

    # Section header pattern
    section_patterns = {
        'summary':
            r'(?i)\n\s*(?:\w+\s+){0,2}(summary|ringkasan|overview|profil|profile|objective|career\s+objective|ringkasan\s+pelamar|about\s+me|personal\s+summary)(?:\s+\w+){0,2}\s*\n',
        'skills':
            r'(?i)\n\s*(?:\w+\s+){0,2}(skills|keahlian|abilities|competencies|technical\s+skills|keahlian\s+pelamar|core\s+competencies|key\s+skills)(?:\s+\w+){0,2}\s*\n',
        'experience':
            r'(?i)\n\s*(?:\w+\s+){0,2}(experience|pengalaman|work\s+experience|employment|career|pengalaman\s+kerja|work\s+history|professional\s+experience)\s*\n',
        'education':
            r'(?i)\n\s*(?:\w+\s+){0,2}(education|pendidikan|academic|riwayat\s+pendidikan|educational\s+background|academic\s+qualification)(?:\s+\w+){0,2}\s*\n'
    }

    # Extract each section
    for section_name, patterns in section_patterns.items():
        sections[section_name] = _extract_section_content(
            text, section_name, patterns)

    return sections


def _extract_section_content(text: str, section_name: str, pattern: List[str]):
    """
    Extract content for a specific section based on header patterns.

    Args:
        text (str): Full text content
        section_name (str): Section name
        pattern (str): Regex patterns for section headers

    Returns:
        str: Extracted section content
        list[Dict]: If section name is "experience". {title:"..", timePlace:"..", points:[".."]}
        list[str]: If section name is "education", list of education.
    """
    section_end_patterns = {
        'summary': [
            r'(?i)\n\s*(\w+(?:\s+\w+)?)(?=\s*\n)'
        ],
        'skills': [
            r'(?i)\n\s*(qualifications|accomplishments|achievements|awards|certifications|projects)',
            r'(?i)\n\s*(experience|pengalaman|education|pendidikan|contact|kontak|references|referensi)'
        ],
        'experience': [
            r'(?i)\n\s*(qualifications|accomplishments|achievements|awards|certifications|projects)',
            r'(?i)\n\s*(skills|keahlian|education|pendidikan|contact|kontak|references|referensi)'
        ],
        'education': [
            r'(?i)\n\s*(qualifications|accomplishments|achievements|awards|certifications|projects)',
            r'(?i)\n\s*(skills|keahlian|experience|pengalaman|contact|kontak|references|referensi)'
        ]
    }

    match = re.search(pattern, text)
    if not match:
        return ""

    start_pos = match.start()

    # Find section end
    next_section_patterns = section_end_patterns[section_name]
    end_pos = len(text)
    for end_pattern in next_section_patterns:
        end_match = re.search(
            end_pattern, text[start_pos + len(match.group()):])
        if end_match:
            end_pos = start_pos + len(match.group()) + end_match.start()
            break

    # Extract content
    content = text[start_pos:end_pos]

    # Remove header line
    content = re.sub(pattern, '', content, count=1)
    content = content.strip()

    if content:
        if (section_name == "experience"):
            return group_experience(content)
        if (section_name == "education"):
            return group_education(content)
        return content

    return ""


def group_experience(experience_text: str) -> List[Dict[str, any]]:
    """
    Group experience text into structured JSON format.

    Args:
        experience_text (str): Raw experience text from CV

    Returns:
        List[Dict]: List of experience dictionaries with title, timePlace, and points
    """
    if not experience_text:
        return []

    lines = [line.strip()
             for line in experience_text.split('\n') if line.strip()]
    experiences = []
    current_experience = None

    invalid_title_pattern = r'(?i)^(qualifications|accomplishments|achievements|awards|certifications|projects|skills|keahlian|education|pendidikan|contact|kontak|references|referensi|interest)'

    def is_invalid_title(title: str) -> bool:
        """Check if title matches invalid patterns using regex"""
        return bool(re.match(invalid_title_pattern, title.strip()))

    def is_title_case_line(line: str) -> bool:
        """Check if line has title case (each word starts with capital letter)"""
        if not line:
            return False
        # Remove common punctuation and numbers for title case check
        clean_line = re.sub(r'[^\w\s]', '', line)
        words = clean_line.split()
        if not words:
            return False
        # Check if most words (at least 70%) start with capital letter
        capital_words = sum(1 for word in words if word and word[0].isupper())
        return capital_words / len(words) >= 0.7

    def is_sentence(line: str) -> bool:
        """Check if line is a sentence (starts with capital, ends with period/punctuation)"""
        return line and line[0].isupper() and (line.endswith('.') or line.endswith(',') or len(line) > 50)

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if new experience title
        if is_title_case_line(line) and not is_sentence(line):
            # Save previous experience
            if current_experience and len(current_experience['points']) > 0:
                experiences.append(current_experience)

            # New experience
            current_experience = {
                'title': line,
                'timePlace': '',
                'points': []
            }

            # timePlace
            j = i + 1
            timePlace_parts = []
            while j < len(lines):
                next_line = lines[j]
                if is_title_case_line(next_line) and not is_sentence(next_line):
                    timePlace_parts.append(next_line)
                    j += 1
                elif is_sentence(next_line):
                    break
                else:
                    # Might be part of timePlace
                    if next_line and not is_sentence(next_line):
                        timePlace_parts.append(next_line)
                    j += 1

            current_experience['timePlace'] = ' '.join(timePlace_parts)
            i = j - 1

        # Collect experience points
        elif current_experience and is_sentence(line) and not is_title_case_line(line):
            j = i + 1
            while j < len(lines) and not line.endswith('.'):
                next_line = lines[j]
                line += next_line
                j += 1
            i = j - 1

            current_experience['points'].append(line)

        i += 1

    # Add last experience
    if current_experience and not is_invalid_title(current_experience['title']) and len(current_experience['points']) > 0:
        experiences.append(current_experience)

    return experiences


def group_education(education_text: str) -> List[str]:
    """
    Group education text into array of clean text entries.

    Args:
        education_text (str): Raw education text from CV

    Returns:
        List[str]: List of education entries as single line text
    """
    if not education_text:
        return []

    entries = re.split(r'\n\s*\n', education_text)
    cleaned_entries = []
    for entry in entries:
        if entry.strip():
            clean_entry = re.sub(r'\s*\n\s*', ' ', entry.strip())
            clean_entry = re.sub(r'\s+', ' ', clean_entry)
            cleaned_entries.append(clean_entry)

    return cleaned_entries


def main():
    """
    Main function for testing and demonstrating the PDF extraction functionality.
    """

    print("\nTesting Regex Pattern Generation:")
    print("-" * 40)
    pdf_path = "data/ACCOUNTANT/10674770.pdf"
    regex_result = extract_pdf_to_regex_string(pdf_path)

    if regex_result:
        print("===Successfully extracted sections:===")
        for section, content in regex_result.items():
            if content:
                if (section == "experience"):
                    print(f"=={section.upper()}:==")
                    for exp in content:
                        print(f"title: {exp['title']}")
                        print(f"timePlace: {exp['timePlace']}")
                        print("Points:")
                        i = 0
                        for point in exp['points']:
                            i += 1
                            print(f"{i}.{point}")
                        print()
                    print()
                elif (section == "education"):
                    print(f"=={section.upper()}:==")
                    i = 0
                    for education in content:
                        i += 1
                        print(f"{i}.{education}")
                    print()
                else:
                    print(f"=={section.upper()}:==\n {content}")
                    print()

    else:
        print("==No regex patterns generated - PDF not found==")

    print("\n===Testing complete!===")
    print("="*60)


if __name__ == "__main__":
    main()
