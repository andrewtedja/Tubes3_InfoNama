import flet as ft
import os
import sys
import re
from typing import Dict, List, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.extract_pdf_regex import extract_pdf_to_regex_string


class SummaryPage:
    def __init__(self, page: ft.Page, applicant_data: Dict, main_gui_instance):
        self.page = page
        self.applicant_data = applicant_data
        self.main_gui = main_gui_instance
        self.cv_sections = None

        # Store the current page state before clearing
        self.previous_controls = self.page.controls.copy()

        self.load_cv_sections()
        self.show_summary_page()

    def load_cv_sections(self):
        """Load CV sections from PDF using extract_pdf_regex"""
        if self.applicant_data and self.applicant_data.get('cv_path'):
            try:
                cv_path = self.applicant_data['cv_path']
                self.cv_sections = extract_pdf_to_regex_string(cv_path)
                print(f"Successfully loaded CV sections for: {cv_path}")
            except Exception as e:
                print(f"Error extracting CV sections: {e}")
                self.cv_sections = None
        else:
            print("No CV path found in applicant data")
            self.cv_sections = None

    def create_header_section(self):
        """Create the header section with applicant info"""
        if not self.applicant_data:
            return ft.Container(
                content=ft.Text("No applicant data available", color="#8D847D")
            )

        # Format data from passed applicant_data
        first_name = self.applicant_data.get('first_name', '')
        last_name = self.applicant_data.get('last_name', '') or ''
        full_name = f"{first_name} {last_name}".strip()

        birthdate = self.applicant_data.get('date_of_birth', 'N/A')
        address = self.applicant_data.get('address', 'N/A')
        phone = self.applicant_data.get('phone_number', 'N/A')

        # Date formatting
        if hasattr(birthdate, 'strftime'):
            birthdate = birthdate.strftime('%d-%m-%Y')

        return ft.Container(
            width=850,
            bgcolor="#A8A8A8",
            border_radius=ft.border_radius.all(12),
            padding=ft.padding.all(25),
            margin=ft.margin.symmetric(vertical=10),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text(full_name or "Unknown Name", size=28,
                            weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Divider(height=1, color="#FFFFFF70"),
                    ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_TODAY,
                                color="#FFFFFF70", size=16),
                        ft.Text(f"Birthdate: {birthdate}",
                                size=14, color=ft.Colors.WHITE),
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON,
                                color="#FFFFFF70", size=16),
                        ft.Text(f"Address: {address}",
                                size=14, color=ft.Colors.WHITE),
                    ], spacing=8),
                    ft.Row([
                        ft.Icon(ft.Icons.PHONE, color="#FFFFFF70", size=16),
                        ft.Text(f"Phone: {phone}", size=14,
                                color=ft.Colors.WHITE),
                    ], spacing=8),
                ]
            )
        )

    def create_skills_section(self):
        """Create the skills section with all skill chips"""
        if not self.cv_sections or not self.cv_sections.get('skills'):
            return ft.Container(
                width=850,
                padding=ft.padding.symmetric(vertical=15),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Text("Skills:", size=20,
                                weight=ft.FontWeight.BOLD, color="#4a4441"),
                        ft.Container(
                            width=850,
                            bgcolor="#F5F5F5",
                            border_radius=ft.border_radius.all(12),
                            padding=ft.padding.all(25),
                            content=ft.Text(
                                "No skills information found in CV", size=14, color="#8D847D")
                        )
                    ]
                )
            )

        skills_text = self.cv_sections['skills']
        skills_list = []

        potential_skills = re.split(r'[;,\n•\-\*]', skills_text)

        for skill in potential_skills:
            skill = skill.strip()
            if skill and len(skill) > 1:
                skills_list.append(skill)

        if not skills_list:
            return ft.Container(
                width=850,
                padding=ft.padding.symmetric(vertical=15),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Text("Skills:", size=20,
                                weight=ft.FontWeight.BOLD, color="#4a4441"),
                        ft.Container(
                            width=850,
                            bgcolor="#F5F5F5",
                            border_radius=ft.border_radius.all(12),
                            padding=ft.padding.all(25),
                            content=ft.Text(
                                "Could not extract specific skills from CV", size=14, color="#8D847D")
                        )
                    ]
                )
            )

        skill_chips = []
        for skill in skills_list:
            skill_chips.append(
                ft.Container(
                    bgcolor="#A8A8A8",
                    border_radius=ft.border_radius.all(20),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    margin=ft.margin.all(3),
                    content=ft.Text(
                        skill, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)
                )
            )

        return ft.Container(
            width=850,
            padding=ft.padding.symmetric(vertical=15),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Text("Skills:", size=20,
                            weight=ft.FontWeight.BOLD, color="#4a4441"),
                    ft.Container(
                        width=850,
                        bgcolor="#F5F5F5",
                        border_radius=ft.border_radius.all(12),
                        padding=ft.padding.all(25),
                        content=ft.Row(
                            spacing=8,
                            wrap=True,
                            controls=skill_chips
                        )
                    )
                ]
            )
        )

    def create_experience_section(self):
        """Create the job history section with all experiences"""
        if not self.cv_sections or not self.cv_sections.get('experience'):
            return ft.Container(
                width=850,
                padding=ft.padding.symmetric(vertical=15),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Text("Job History:", size=20,
                                weight=ft.FontWeight.BOLD, color="#4a4441"),
                        ft.Container(
                            width=850,
                            bgcolor="#A8A8A8",
                            border_radius=ft.border_radius.all(12),
                            padding=ft.padding.all(25),
                            content=ft.Text("No work experience information found in CV",
                                            size=14, color=ft.Colors.WHITE)
                        )
                    ]
                )
            )

        experience_data = self.cv_sections['experience']
        experience_containers = []

        if isinstance(experience_data, list) and experience_data:
            # Display experience entries
            for i, exp in enumerate(experience_data):
                title = exp.get('title', 'N/A')
                time_place = exp.get('timePlace', 'N/A')
                points = exp.get('points', [])

                # Job bullet points
                point_controls = []
                for point in points:
                    point_controls.append(
                        ft.Row([
                            ft.Text("•", size=12, color="#FFFFFF70"),
                            ft.Text(point, size=12,
                                    color=ft.Colors.WHITE, expand=True)
                        ], spacing=8)
                    )

                experience_containers.append(
                    ft.Container(
                        width=850,
                        bgcolor="#A8A8A8",
                        border_radius=ft.border_radius.all(12),
                        padding=ft.padding.all(25),
                        margin=ft.margin.symmetric(vertical=8),
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Text(
                                    title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(time_place, size=14,
                                        color="#FFFFFF70", italic=True),
                                ft.Divider(height=1, color="#FFFFFF30"),
                                *point_controls
                            ]
                        )
                    )
                )
        else:
            experience_containers.append(
                ft.Container(
                    width=850,
                    bgcolor="#A8A8A8",
                    border_radius=ft.border_radius.all(12),
                    padding=ft.padding.all(25),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text("Experience Available", size=18,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(str(experience_data), size=12,
                                    color=ft.Colors.WHITE),
                        ]
                    )
                )
            )

        return ft.Container(
            width=850,
            padding=ft.padding.symmetric(vertical=15),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Text("Job History:", size=20,
                            weight=ft.FontWeight.BOLD, color="#4a4441"),
                    *experience_containers
                ]
            )
        )

    def create_education_section(self):
        """Create the education section with all education entries"""
        if not self.cv_sections or not self.cv_sections.get('education'):
            return ft.Container(
                width=850,
                padding=ft.padding.symmetric(vertical=15),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Text("Education:", size=20,
                                weight=ft.FontWeight.BOLD, color="#4a4441"),
                        ft.Container(
                            width=850,
                            bgcolor="#A8A8A8",
                            border_radius=ft.border_radius.all(12),
                            padding=ft.padding.all(25),
                            content=ft.Text("No education information found in CV",
                                            size=14, color=ft.Colors.WHITE)
                        )
                    ]
                )
            )

        education_data = self.cv_sections['education']
        education_containers = []

        if isinstance(education_data, list) and education_data:
            # Display education entries
            for i, education_text in enumerate(education_data):
                # Degree and institution patterns
                degree_match = re.search(
                    r'([A-Za-z\s]+(?:Engineering|Science|Arts|Business|Management|Technology|Informatics|Bachelor|Master|PhD|Doctorate))', education_text)
                institution_match = re.search(
                    r'(?:Institut|University|College|Universitas|School)[\s\w]+', education_text)
                year_match = re.search(
                    r'(20\d{2}[-\s]*20\d{2}|19\d{2}[-\s]*20\d{2}|20\d{2}|19\d{2})', education_text)

                degree = degree_match.group(1).strip(
                ) if degree_match else f"Education Entry {i+1}"
                institution = institution_match.group(
                    0).strip() if institution_match else "Institution"
                year = year_match.group(
                    0) if year_match else "Year not specified"

                education_containers.append(
                    ft.Container(
                        width=850,
                        bgcolor="#A8A8A8",
                        border_radius=ft.border_radius.all(12),
                        padding=ft.padding.all(25),
                        margin=ft.margin.symmetric(vertical=8),
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Text(
                                    degree, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Text(f"📍 {institution}", size=14,
                                        color="#FFFFFF70", italic=True),
                                ft.Text(f"📅 {year}", size=12,
                                        color="#FFFFFF70"),
                                ft.Divider(height=1, color="#FFFFFF30"),
                                ft.Text(education_text, size=12,
                                        color="#FFFFFF"),
                            ]
                        )
                    )
                )
        else:
            # Single education entry
            education_text = str(education_data)
            degree_match = re.search(
                r'([A-Za-z\s]+(?:Engineering|Science|Arts|Business|Management|Technology|Informatics|Bachelor|Master|PhD|Doctorate))', education_text)
            institution_match = re.search(
                r'(?:Institut|University|College|Universitas|School)[\s\w]+', education_text)
            year_match = re.search(
                r'(20\d{2}[-\s]*20\d{2}|19\d{2}[-\s]*20\d{2}|20\d{2}|19\d{2})', education_text)

            degree = degree_match.group(1).strip(
            ) if degree_match else "Education Information"
            institution = institution_match.group(
                0).strip() if institution_match else "Institution"
            year = year_match.group(0) if year_match else "Year not specified"

            education_containers.append(
                ft.Container(
                    width=850,
                    bgcolor="#A8A8A8",
                    border_radius=ft.border_radius.all(12),
                    padding=ft.padding.all(25),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(
                                degree, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f"📍 {institution}", size=14,
                                    color="#FFFFFF70", italic=True),
                            ft.Text(f"📅 {year}", size=12, color="#FFFFFF70"),
                            ft.Divider(height=1, color="#FFFFFF30"),
                            ft.Text(education_text, size=12, color="#FFFFFF"),
                        ]
                    )
                )
            )

        return ft.Container(
            width=850,
            padding=ft.padding.symmetric(vertical=15),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Text("Education:", size=20,
                            weight=ft.FontWeight.BOLD, color="#4a4441"),
                    *education_containers
                ]
            )
        )

    def show_summary_page(self):
        """Display the complete summary page"""
        self.page.controls.clear()

        # Applicant name
        first_name = self.applicant_data.get(
            'first_name', '') if self.applicant_data else ''
        last_name = self.applicant_data.get(
            'last_name', '') if self.applicant_data else ''
        full_name = f"{first_name} {last_name}".strip() or "CV Summary"

        # Main content with scrollable
        main_content = ft.Container(
            width=950,
            padding=ft.padding.all(30),
            content=ft.Column(
                spacing=25,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    # Back button and title row
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_size=28,
                            on_click=self.go_back,
                            tooltip="Back to Search",
                            style=ft.ButtonStyle(
                                bgcolor="#4a4441",
                                color=ft.Colors.WHITE,
                                shape=ft.CircleBorder(),
                            )
                        ),
                        ft.Text(f"CV Summary", size=36, weight=ft.FontWeight.BOLD,
                                color="#4a4441", expand=True),
                    ], alignment=ft.MainAxisAlignment.START),

                    # Header section applicant info
                    self.create_header_section(),

                    # Skills section
                    self.create_skills_section(),

                    # Job history section
                    self.create_experience_section(),

                    # Education section
                    self.create_education_section(),

                    ft.Container(height=30),
                ]
            )
        )

        self.page.scroll = ft.ScrollMode.AUTO
        self.page.add(main_content)
        self.page.update()

    def go_back(self, e):
        """Return to the main search page while preserving the search results"""
        # Clear current page
        self.page.controls.clear()

        # Restore previous page
        self.page.controls.extend(self.previous_controls)
        self.page.update()
