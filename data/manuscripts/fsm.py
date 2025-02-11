from transitions import Machine

class ManuscriptFSM:
    states = [
        'Submitted', 'Rejected', 'Withdrawn', 'Referee_Review',
        'Author_Revisions', 'Editor_Review', 'Copy_Edit',
        'Author_Review', 'Formatting', 'Published', 'Update'
    ]
    
    def __init__(self):
        self.machine = Machine(model=self, states=self.states, initial='Submitted')
        
        # Define transitions
        self.machine.add_transition('assign_referee', 'Submitted', 'Referee_Review')
        self.machine.add_transition('reject', ['Submitted', 'Referee_Review'], 'Rejected')
        self.machine.add_transition('withdraw', self.states, 'Withdrawn')
        self.machine.add_transition('accept_with_revisions', 'Referee_Review', 'Author_Revisions')
        self.machine.add_transition('accept', 'Referee_Review', 'Copy_Edit')
        self.machine.add_transition('submit_revisions', 'Author_Revisions', 'Editor_Review')
        self.machine.add_transition('editor_accept', 'Editor_Review', 'Copy_Edit')
        self.machine.add_transition('complete_copy_edit', 'Copy_Edit', 'Author_Review')
        self.machine.add_transition('complete_author_review', 'Author_Review', 'Formatting')
        self.machine.add_transition('complete_formatting', 'Formatting', 'Published')
        self.machine.add_transition('submit_update', 'Update', 'Editor_Review')
        
        # Editor Move allows jumping to any state
        for state in self.states:
            for target_state in self.states:
                if state != target_state:
                    self.machine.add_transition('editor_move', state, target_state)

    def get_state(self):
        return self.state

# Example usage
fsm = ManuscriptFSM()
print("Initial State:", fsm.get_state())

fsm.assign_referee()
print("After Assigning Referee:", fsm.get_state())

fsm.accept_with_revisions()
print("After Accepting with Revisions:", fsm.get_state())

fsm.submit_revisions()
print("After Submitting Revisions:", fsm.get_state())

fsm.editor_accept()
print("After Editor Accepts:", fsm.get_state())

fsm.complete_copy_edit()
print("After Copy Edit:", fsm.get_state())

fsm.complete_author_review()
print("After Author Review:", fsm.get_state())

fsm.complete_formatting()
print("After Formatting:", fsm.get_state())
