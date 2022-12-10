from textual.widgets import ListView, ListItem, Label


class PartitionList(ListView):
    def __init__(self, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.append(ListItem(Label("One")))
        self.append(ListItem(Label("Two")))
        self.append(ListItem(Label("Three")))
        self.append(ListItem(Label("Four")))