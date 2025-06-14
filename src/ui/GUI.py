import flet as ft
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ats_processor import ATSProcessor

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

        # Nanti ini yang di ganti sama data dari DB
        self.cv_dataset = [
            {
                'id': 1,
                'name': 'Asep', 
                'cv_text': 'Senior developer in Chicago with experience in React Native, Express, and modern HTML. Loves Python.'
            },
            {
                'id': 2,
                'name': 'Lababo', 
                'cv_text': 'Junior developer from Tennessee skilled in React Native American and Python, Loves SQL.'
            },
            {
                'id': 3,
                'name': 'Kolman', 
                'cv_text': 'Project manager in New York who uses Express for backend services. Familiar with SQL databases.'
            }
        ]

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
        self.search_status = ft.Text("Enter keywords to begin your search.", color="#8D847D") 
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
        self.search_status.value = "Scanning CVs..."
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
        
        # STORE ALL RESULTS ARRAY
        all_results = []
            
        # NANTI BISA TAMBA IF/ELSE BUAT self.selected_algorithm


        # Loop through your CVs
        for cv in self.cv_dataset:
            self.processor.load_cv(cv['cv_text'])
            total_exact, total_fuzzy = self.processor.search_keywords(keywords_str)
            total_matches = total_exact + total_fuzzy

            if total_matches > 0:
                # Format the summary for the card display
                summary_list = []
                for kw, count in self.processor.exact_results.items():
                    if count > 0:
                        summary_list.append(f"{kw}: {count} (exact)")
                
                for kw, res in self.processor.fuzzy_results.items():
                    if res['count'] > 0:
                        summary_list.append(f"{kw}: {res['count']} (fuzzy)")
                
                # Append formatted result
                all_results.append({
                    'name': cv['name'],
                    'match_count': total_matches,
                    'summary': summary_list
                })

        # ================ Sort results by the highest match count ================
        sorted_results = sorted(all_results, key=lambda x: x['match_count'], reverse=True)
        top_results = sorted_results[:top_n]
        
        # Display the results
        self.search_status.value = f"Found {len(top_results)} relevant CVs."
        if not top_results:
            self.results_grid.controls.append(ft.Container(
                content=ft.Text("No matching CVs found."),
                alignment=ft.alignment.center)
            )
        else:
            for result in top_results:
                card = self.create_result_card(
                    name=result['name'],
                    match_count=result['match_count'],
                    matched_keywords_summary=result['summary']
                )
                self.results_grid.controls.append(card)
        
        # Adjust grid height based on =>  num of results
        rows_needed = (len(self.results_grid.controls) + self.results_grid.runs_count - 1) // self.results_grid.runs_count
        self.results_grid.height = rows_needed * 380
        self.page.update()


    def create_result_card(self, name, match_count, matched_keywords_summary):
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
                                on_click=lambda e, n=name: self.view_cv_clicked(n),
                                style=ft.ButtonStyle(color="#141414", side=ft.BorderSide(1, "#141414"))
                            ),

                            ft.ElevatedButton(
                                text="Summary", icon=ft.Icons.VISIBILITY, 
                                bgcolor="#141414", color=ft.Colors.WHITE,
                                on_click=lambda e, n=name: self.view_summary_clicked(n)
                            ),
                        ],
                    ),
                ]
            )
        )

    # Nanti navigate ke halaman summary
    # def view_summary_clicked(self, applicant_name):

    def view_cv_clicked(self, applicant_name):
        """Placeholder logic for opening the CV file."""
        print(f"Logic to find and open the CV file for {applicant_name} goes here.")

    def view_summary_clicked(self,applicant_name):
        """Placeholder logic for viewing the summary"""
        print(f"Logic to find and view the summarized CV for {applicant_name} goes here.")

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
