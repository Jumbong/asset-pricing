from view.start_view import StartView

if __name__ == "__main__":
    current_view = StartView()
    while current_view:
        current_view.display()
        current_view=current_view.choose()
        
        
        