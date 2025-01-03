class ConversationContext:
    def __init__(self):
        self.context = {}

    def update_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key, None)
    
    def clear_context(self):
        self.context = {}
        
    def __str__(self):
        pass
    
    def __repr__(self):
        pass
    
    def __eq__(self, other):
        pass
    
    def __ne__(self, other):
        pass
    
    def __hash__(self):
        pass
    
    def __getitem__(self, key):
        pass
    