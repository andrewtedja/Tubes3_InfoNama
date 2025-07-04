import flet as ft
import time
import sys
import os
import webbrowser
from pathlib import Path
from summary_page import SummaryPage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ats_processor import ATSProcessor
from database import loader

class GUI:
    def __init__(self, page: ft.Page):
        # ============================ PAGE UI =============================
        self.page = page
        self.page.title = "CV Analyzer App"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.window.width = 950
        self.page.window.height = 800
        self.page.bgcolor = "#FFFFFF" 
        self.page.scroll = ft.ScrollMode.ADAPTIVE 

        # =================== ATS Processor ===================
        self.processor = ATSProcessor(fuzzy_threshold=0.65)

        # =================== Load DB ===================
        self.cv_dataset = loader.load_all_data()

        # ==================== KEYWORDS INPUT =======================
        self.keywords_input = ft.TextField(
            label="Keywords",
            hint_text="e.g., Python, React, SQL",
            expand=True,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(8),
            border_color="#4a4441",

            label_style=ft.TextStyle(color="#4a4441"),
            hint_style=ft.TextStyle(color="#8D847D"),
            text_style=ft.TextStyle(color="#4a4441"),
        )

        # Buat selected
        self.selected_algorithm = "KMP"
        self.search_algo_buttons = ft.Row(spacing=10)
        self.update_algo_buttons()

        # ==================== TOP MATCHES =======================
        self.top_matches_input = ft.TextField(
            label="Top Matches",
            value="5",
            width=150,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(8),
            border_color="#4a4441",
            keyboard_type=ft.KeyboardType.NUMBER,

            label_style=ft.TextStyle(color="#4a4441"),
            text_style=ft.TextStyle(color="#4a4441"),
        )

        # ==================== SEARCH =======================
        self.search_button = ft.ElevatedButton(
            text="Search",
            on_click=self.search_clicked,
            icon=ft.Icons.SEARCH,
            width=300,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15,
                bgcolor="#141414",
                color=ft.Colors.WHITE,
            )
        )
        self.search_status = ft.Text(
            "Enter keywords to begin your search.", color="#8D847D")
        self.results_grid = ft.GridView(
            expand=False,
            runs_count=3,
            max_extent=280,
            child_aspect_ratio=0.75,
            spacing=15,
            run_spacing=15,
        )
        self.selected_algo_text = ft.Text(
            value=f"Current Algorithm: {self.selected_algorithm}",
            size=14,
            color="#4a4441",
            italic=True,
        )

        # DISPLAY UI
        self.page.add(self.build_ui())

        # DUMMY DATA GRID
        # self.populate_dummy_grid()

    # ==================== SELECT ALGO TOGGLE =====================
    def update_algo_buttons(self):
        """Rebuilds the search algorithm buttons with style depending on selection."""
        def make_algo_button(label: str) -> ft.TextButton:
            is_selected = self.selected_algorithm == label
            return ft.TextButton(
                text=label,
                on_click=lambda e, l=label: self.on_algo_change(l),
                style=ft.ButtonStyle(
                    bgcolor="#141414" if is_selected else "#FFFFFF",
                    color="#FFFFFF" if is_selected else "#4a4441",
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(color="#141414", width=1),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                )
            )

        self.search_algo_buttons.controls = [
            make_algo_button("KMP"),
            make_algo_button("BM"),
            make_algo_button("Aho-Corasick")
        ]
        self.page.update()

    def on_algo_change(self, selected: str):
        self.selected_algorithm = selected
        self.selected_algo_text.value = f"Current Algorithm: {selected}"
        self.processor.set_algorithm(selected)
        self.update_algo_buttons()
        self.page.update()

    # Ini buat dummy doang show gridnya
    # ==================== DUMMY DATA GRID =====================
    # def populate_dummy_grid(self):
    #     """Populates the grid with placeholder data to show the layout."""
    #     dummy_files = [
    #         {'name': 'Farhan', 'count': 4, 'summary': ['React: 2', 'Express: 2']},
    #         {'name': 'Aland', 'count': 1, 'summary': ['React: 1']},
    #         {'name': 'Ariel', 'count': 1, 'summary': ['Express: 1']},
    #         {'name': 'Budi', 'count': 3, 'summary': ['Python: 2', 'SQL: 1']},
    #         {'name': 'Cici', 'count': 2, 'summary': ['HTML: 1', 'CSS: 1']},
    #         {'name': 'Dani', 'count': 2, 'summary': ['Express: 1', 'Node.js: 1']},
    #     ]

    #     self.results_grid.controls.clear()
    #     for file in dummy_files:
    #         card = self.create_result_card(
    #             name=file['name'],
    #             match_count=file['count'],
    #             matched_keywords_summary=file['summary']
    #         )
    #         self.results_grid.controls.append(card)

    #     self.results_grid.height = (len(self.results_grid.controls) / self.results_grid.runs_count) * 380
    #     self.page.update()

    # ==================== SEARCH LOGIC =====================
    def search_clicked(self, e):
        """Callback for the search button. Connect ke ATSProcessor"""
        self.results_grid.controls.clear()
        self.search_status.value = f"Scanning CVs with {self.selected_algorithm}..."
        self.page.update()

        keywords_str = self.keywords_input.value

        try:
            top_n = int(self.top_matches_input.value)
        except (ValueError, TypeError):
            self.search_status.value = "Top Matches must be a number."
            self.page.update()
            return

        if not keywords_str:
            self.search_status.value = "Please enter keywords to search."
            # self.populate_dummy_grid()
            return

        # Top results
        top_results, exact_match_time, fuzzy_match_time = self.processor.get_top_search_results(
            top_n, keywords_str, self.cv_dataset)

        # Display the results
        self.search_status.value = f"Found {len(top_results)} relevant CVs.\n"
        self.search_status.value += f"Exact Match: {len(self.cv_dataset)} CVs scanned in {exact_match_time}ms.\n"
        
        if (fuzzy_match_time > 0):
            self.search_status.value += f"Fuzzy Match: {len(self.cv_dataset)} CVs scanned in {fuzzy_match_time}ms."

        if not top_results:
            self.results_grid.controls.append(ft.Container(
                content=ft.Text("No matching CVs found."),
                alignment=ft.alignment.center)
            )
        else:
            for result in top_results:
                card = self.create_result_card(
                    data = result['data'],
                    name=result['name'],
                    match_count=result['match_count'],
                    matched_keywords_summary=result['summary']
                )
                self.results_grid.controls.append(card)

        # Adjust grid height based on =>  num of results
        rows_needed = (len(self.results_grid.controls) +
                       self.results_grid.runs_count - 1) // self.results_grid.runs_count
        self.results_grid.height = rows_needed * 380
        self.page.update()

    def create_result_card(self, data, name, match_count, matched_keywords_summary):
        """Display card search result."""
        keywords_display_list = [
            ft.Text(f"• {item}", size=12, color="#8D847D") for item in matched_keywords_summary
        ]

        return ft.Container(
            padding=20,
            border_radius=ft.border_radius.all(12),
            border=ft.border.all(1, "#D3CFCB"),
            bgcolor=ft.Colors.WHITE,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(name, weight=ft.FontWeight.BOLD, size=22, color="#4a4441"),
                    ft.Divider(height=1, color="#EAE6E3"),
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="#859976", size=18),
                        ft.Text(f"Total Matches: {match_count}", weight=ft.FontWeight.BOLD, size=14, color="#4a4441"),
                    ], spacing=8),

                    ft.Column(spacing=5, controls=[
                        ft.Text("Matched Keywords:", weight=ft.FontWeight.W_500, size=14, color="#4a4441"),
                        *keywords_display_list
                    ]),

                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.OutlinedButton(
                                text="View CV", icon=ft.Icons.DESCRIPTION_OUTLINED,
                                on_click=lambda e, cv_path=data['cv_path']: self.view_cv_clicked(cv_path),
                                style=ft.ButtonStyle(color="#141414", side=ft.BorderSide(1, "#141414"))
                            ),

                            ft.ElevatedButton(
                                text="Summary", icon=ft.Icons.VISIBILITY, 
                                bgcolor="#141414", color=ft.Colors.WHITE,
                                on_click=lambda e, data=data: self.view_summary_clicked(data)
                            ),
                        ],
                    ),
                ]
            )
        )

    # Nanti navigate ke halaman summary
    # def view_summary_clicked(self, applicant_name):

    def view_cv_clicked(self, cv_path):
        """Open the CV file in web browser."""
        
        if cv_path:
            try:
                abs_path = os.path.abspath(cv_path)
                
                if os.path.exists(abs_path):
                    file_url = Path(abs_path).as_uri()
                    webbrowser.open(file_url)
                    print(f"Opening CV: {abs_path}")
                else:
                    print(f"CV file not found: {abs_path}")
                    self.search_status.value = f"CV file not found"
                    self.page.update()
            except Exception as ex:
                print(f"Error opening CV: {ex}")
                self.search_status.value = f"Error opening CV"
                self.page.update()
        else:
            print(f"No CV path found")
            self.search_status.value = f"No CV found"
            self.page.update()

    def view_summary_clicked(self, data):
        """Navigate to the summary page for the selected applicant"""
        try:
            SummaryPage(self.page, data, self)
        except Exception as e:
            print(f"Error opening summary page: {e}")
            self.search_status.value = f"Error loading summary page"
            self.page.update()

    def build_ui(self):
        """Builds the main layout of the application."""
        return ft.Container(
            width=900,
            padding=20,
            content=ft.Column(
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("ATS with Pattern Matching", size=32, weight=ft.FontWeight.BOLD, color="#4a4441"),
                    ft.Row([self.keywords_input, self.top_matches_input], vertical_alignment=ft.CrossAxisAlignment.END),
                    ft.Row([
                        ft.Text("Search Algorithm:", weight=ft.FontWeight.BOLD, size=14, color="#4a4441"), 
                        self.search_algo_buttons],
                        alignment=ft.MainAxisAlignment.CENTER),
                    self.search_button,
                    self.selected_algo_text,
                    ft.Divider(height=5),
                    self.search_status,
                    self.results_grid,
                ],
            )
        )

def main(page: ft.Page):
    GUI(page)

if __name__ == "__main__":
    ft.app(target=main)
