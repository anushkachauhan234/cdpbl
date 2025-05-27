from flask import Flask, render_template, request, redirect, url_for, session
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def evaluate_exit_expression(code):
    match = re.search(r"exit\((.*?)\)", code)
    if match:
        expr = match.group(1)
        try:
            safe_expr = re.sub(r'[^0-9+\-*/(). ]', '', expr)
            result = eval(safe_expr)
            return result
        except Exception:  
            return "Error evaluating expression"
    return "No exit() call found"

def lexer(code):
    token_specification = [
        ('KEYWORD',   r'\b(exit|if|while|return)\b'),
        ('INT',       r'\b\d+\b'),
        ('ID',        r'\b[a-zA-Z_]\w*\b'),
        ('OPERATOR',  r'[+\-*/=<>!]'),
        ('SEPARATOR', r'[(),;{}]'),
        ('SKIP',      r'[ \t\n]+'),
        ('UNKNOWN',   r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        tokens.append({'type': kind, 'value': value})
    return tokens

def syntax_analysis(tokens):
    code = session.get('code', '')
    match = re.search(r"exit\((.*?)\)", code)
    expr = match.group(1) if match else "?"

    tree_lines = build_syntax_tree(expr)

    return [
        "Parsing started.",
        "Detected function call to 'exit'.",
        "Expression inside parentheses parsed.",
        "Syntax tree constructed successfully:",
        ""
    ] + tree_lines

def build_syntax_tree(expr):
    # Support for +, -, *, /
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    output = []
    stack = []

    # Tokenize expression
    tokens = re.findall(r'\d+|[+\-*/()]', expr)

    # Infix to Postfix using Shunting Yard Algorithm
    for token in tokens:
        if token.isdigit():
            output.append(token)
        elif token in precedence:
            while stack and stack[-1] != '(' and precedence[stack[-1]] >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
    while stack:
        output.append(stack.pop())

    # Build tree from postfix
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

    stack = []
    for token in output:
        if token.isdigit():
            stack.append(Node(token))
        else:  # operator
            right = stack.pop()
            left = stack.pop()
            node = Node(token)
            node.left = left
            node.right = right
            stack.append(node)

    # The root of the tree is the last node in stack
    root = stack[-1] if stack else None

    # This function formats the tree for display
    def format_tree(node, indent="", last=True):
        if node is None:
            return []

        tree_str = []
        prefix = indent + ("└── " if last else "├── ")
        tree_str.append(prefix + str(node.value))

        indent += "    " if last else "│   "
        children = [node.left, node.right]
        children = [child for child in children if child]

        for i, child in enumerate(children):
            tree_str += format_tree(child, indent, i == len(children) - 1)

        return tree_str

    return format_tree(root)


 
def semantic_analysis():
    # Simple mock semantic analysis output for demo
    return [
        "Semantic check passed: 'exit' recognized as built-in function.",
        "Operands in expression are valid integers.",
        "No semantic errors found."
    ]

def intermediate_code_generation():
    code = session.get('code', '')
    match = re.search(r"exit\((.*?)\)", code)
    if not match:
        return ["No exit() expression found."]
    
    expr = match.group(1).strip()
    postfix = infix_to_postfix(expr)
    tac, final_temp = generate_tac_from_postfix(postfix)
    tac.append(f"call exit with {final_temp}")
    return tac

def infix_to_postfix(expr):
    precedence = {'+':1, '-':1, '*':2, '/':2, '(':0}
    output = []
    stack = []
    tokens = re.findall(r'\d+|\+|\-|\*|\/|\(|\)', expr)

    for token in tokens:
        if token.isdigit():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and precedence[stack[-1]] >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())
    
    return output

def generate_tac_from_postfix(postfix):
    tac = []
    stack = []
    temp_counter = 1

    for token in postfix:
        if token.isdigit():
            temp_var = f"t{temp_counter}"
            tac.append(f"{temp_var} = {token}")
            stack.append(temp_var)
            temp_counter += 1
        else:
            right = stack.pop()
            left = stack.pop()
            temp_var = f"t{temp_counter}"
            tac.append(f"{temp_var} = {left} {token} {right}")
            stack.append(temp_var)
            temp_counter += 1

    return tac, stack[-1]


def optimization():
    code = session.get('code', '')
    match = re.search(r"exit\((.*?)\)", code)
    if not match:
        return ["No exit() expression found."]
    
    expr = match.group(1)
    
    try:
        # Evaluate the expression safely
        safe_expr = re.sub(r'[^0-9+\-*/(). ]', '', expr)
        result = eval(safe_expr)
        return [
            f"Constant folding applied: {expr} = {result}",
            "Optimized intermediate code:",
            f"call exit with argument {result}"
        ]
    except:
        # Fallback if expression cannot be evaluated directly (e.g. variables)
        return [
            "Expression could not be constant folded.",
            "Falling back to intermediate code generation."
        ] + intermediate_code_generation()


def code_generation():
    code = session.get('code', '')
    match = re.search(r"exit\((.*?)\)", code)
    if not match:
        return ["No exit() expression found."]
    
    expr = match.group(1)
    safe_expr = re.sub(r'[^0-9+\-*/(). ]', '', expr)

    try:
        # Tokenize the expression
        tokens = re.findall(r'\d+|[+\-*/()]', safe_expr)

        # Convert to postfix (Reverse Polish Notation)
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        output = []
        stack = []

        for token in tokens:
            if token.isdigit():
                output.append(token)
            elif token in precedence:
                while stack and stack[-1] != '(' and precedence[stack[-1]] >= precedence[token]:
                    output.append(stack.pop())
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
        while stack:
            output.append(stack.pop())

        # Generate code from postfix
        asm_code = []
        reg_count = 1
        stack = []

        for token in output:
            if token.isdigit():
                reg = f"R{reg_count}"
                asm_code.append(f"LOAD {reg}, #{token}")
                stack.append(reg)
                reg_count += 1
            else:
                right = stack.pop()
                left = stack.pop()
                reg = f"R{reg_count}"
                if token == '+':
                    asm_code.append(f"ADD {reg}, {left}, {right}")
                elif token == '-':
                    asm_code.append(f"SUB {reg}, {left}, {right}")
                elif token == '*':
                    asm_code.append(f"MUL {reg}, {left}, {right}")
                elif token == '/':
                    asm_code.append(f"DIV {reg}, {left}, {right}")
                stack.append(reg)
                reg_count += 1

        asm_code.append(f"CALL exit, {stack[-1]}")
        return asm_code

    except Exception as e:
        return ["Error generating assembly code.", str(e)]


def linking():
    # Mock linking output
    return [
        "Linking with standard libraries.",
        "Final executable generated successfully."
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.form['code']
    session['code'] = code

    eval_result = evaluate_exit_expression(code)
    main_output = f"Result of evaluating: {eval_result}"
    session['main_output'] = main_output

    tokens = lexer(code)
    session['tokens'] = tokens

    # Default phase output is lexical tokens formatted
    phase_name = 'lexical'
    phase_output = format_lexical_output(tokens)
    session['phase_name'] = phase_name
    session['phase_output'] = phase_output

    return render_template('phase_output.html',
                           main_output=main_output,
                           phase_name=phase_name,
                           phase_output=phase_output)

def format_lexical_output(tokens):
    # Show tokens as a list, one token per line: Type: value
    lines = [f"{t['type']:10} : {t['value']}" for t in tokens]
    return '\n'.join(lines)

def format_list_output(lines):
    # Just join list of lines with newlines for display
    return '\n'.join(lines)

@app.route('/phase/<phase_name>')
def phase_output(phase_name):
    code = session.get('code', '')
    main_output = session.get('main_output', '')

    if not code:
        return redirect(url_for('index'))

    tokens = session.get('tokens', [])

    if phase_name == 'lexical':
        phase_output = format_lexical_output(tokens)
    elif phase_name == 'syntax':
        phase_output = format_list_output(syntax_analysis(tokens))
    elif phase_name == 'semantic':
        phase_output = format_list_output(semantic_analysis())
    elif phase_name == 'intermediate':
        phase_output = format_list_output(intermediate_code_generation())
    elif phase_name == 'optimization':
        phase_output = format_list_output(optimization())
    elif phase_name == 'codegen':
        phase_output = format_list_output(code_generation())
    elif phase_name == 'linking':
        phase_output = format_list_output(linking())
    else:
        phase_output = "Invalid phase selected."

    session['phase_name'] = phase_name
    session['phase_output'] = phase_output

    return render_template('phase_output.html',
                           main_output=main_output,
                           phase_name=phase_name,
                           phase_output=phase_output)

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
