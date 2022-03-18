import functools as ft

class State:
    def __init__(self, name) -> None:
        self.name = name
        self.start = False
        self.final = False
        self.transition_rules = dict()

    #maps a state to a symbol. Can map multiple states to same symbol
    def add_rule(self, reading_symbol, destination_state):
        if reading_symbol in self.transition_rules:
            self.transition_rules[reading_symbol].append(destination_state)
        else:
            self.transition_rules[reading_symbol] = [destination_state]

    #return next symbol if transition rule exists
    def read_symbol(self, reading_symbol):
        if reading_symbol in self.transition_rules:
            return self.transition_rules[reading_symbol]
        return [None]

    def set_final(self, isFinal):
        self.final = isFinal

    def set_start(self, isStart):
        self.start = isStart

    def is_final(self):
        return self.final

    def __str__(self) -> str:
        return ', '.join(['Name: ' + self.name, 
            'Start: ' + str(self.start), 
            'Final: ' + str(self.final),
            'Transition Rules: ' + ', '.join([r + ':' + self.read_symbol(r).name for r in self.transition_rules])])


class NFA:
    def __init__(self) -> None:
        self.states = {}
        self.alphabet = set()
        self.start = None
        self.new()

    #creates a new NFA as specified by input NFA file.
    def new(self, nfa_file_name='nfa.txt'):
        self.states = {}
        self.alphabet = set()
        self.start = None
        with open(nfa_file_name) as nfa_file:
            #read states
            state_name_list = nfa_file.readline().rstrip().split(',')
            for state_name in state_name_list: self.states[state_name] = State(state_name)
            #read alphabet (empty string @ always included)
            self.alphabet.add('@')
            letters = nfa_file.readline().rstrip().split(',')
            for l in letters: self.alphabet.add(l)
            #set start state
            start_state = nfa_file.readline().rstrip()
            self.states[start_state].set_start(True)
            self.start = self.states[start_state]
            #set final state(s)
            final_states = nfa_file.readline().rstrip().split(',')
            for final_state in final_states: self.states[final_state].set_final(True)
            #read in all transition rules
            line = nfa_file.readline()
            while line:
                rule = line.rstrip().split(',')
                self.states[rule[0]].add_rule(rule[1], self.states[rule[2]])
                line = nfa_file.readline()
            nfa_file.close()

    #simulates NFA for every string in input file and writes results to output file.
    def run(self, input_file_name='input.txt', output_file_name='output.txt'):
        #clear output file
        with open(output_file_name, 'w') as out:
                    out.truncate(0)
                    out.close()
        #read input file, follow transition rules for each string in file and write result to output.
        with open(input_file_name) as input_file:
            with open(output_file_name, 'w') as out:
                for string in input_file:
                    result = self.simulate(self.start, string.rstrip())
                    if result:
                        out.write('accept\n')
                    else:
                        out.write('reject\n')
                out.close()
            input_file.close()

    #recursively simulate string on NFA start state
    #explanation:
    #simulates every possible path on the nfa and returns the results of all paths in a list.
    #return the result of a reduce with or that checks if any one of those paths accepts.
    def simulate(self, current, string, empty_cycle=set()):
        #kills path if no transition rule for previous symbol or path is @ cycle.
        if current == None or current in empty_cycle:
            return False
        if not string:
            return current.is_final()
        next_states = current.read_symbol(string[0])
        next_results = [self.simulate(s, string[1:]) for s in next_states]
        #always try and use empty string
        empty_next = current.read_symbol('@')
        #keep track of states visited with @. Prevents infinite recursion bc of @ cycles.
        new_empty_cycle = empty_cycle.copy()
        new_empty_cycle.add(current)
        empty_results = [self.simulate(s, string, new_empty_cycle) for s in empty_next]
        #returns (reduced results from trying next symbol) or (reduced results from trying empty string)
        return ft.reduce(lambda a, b: a or b, next_results) or ft.reduce(lambda a, b: a or b, empty_results)

    def __str__(self) -> str:
        return 'States:\n' + '\n'.join(['  ' + '\n  '.join([str(self.states[s]) for s in self.states]), 
            'Alphabet: {' + ', '.join([s for s in self.alphabet]) + '}'])


def main():
    test_NFA = NFA()
    test_NFA.run()


if __name__ == '__main__':
    main()
