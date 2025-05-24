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
    # Simple mock syntax analysis output for demo
    return [
        "Parsing started.",
        "Detected function call to 'exit'.",
        "Expression inside parentheses parsed as addition operation.",
        "Syntax tree constructed successfully."
    ]

def semantic_analysis():
    # Simple mock semantic analysis output for demo
    return [
        "Semantic check passed: 'exit' recognized as built-in function.",
        "Operands in expression are valid integers.",
        "No semantic errors found."
    ]

def intermediate_code_generation():
    # Mock intermediate representation
    return [
        "t1 = 5",
        "t2 = 2",
        "t3 = t1 + t2",
        "call exit with argument t3"
    ]

def optimization():
    # Mock optimization steps
    return [
        "Constant folding applied: 5 + 2 = 7",
        "Optimized intermediate code:",
        "call exit with argument 7"
    ]

def code_generation():
    # Mock assembly-like code generation
    return [
        "LOAD R1, #5",
        "LOAD R2, #2",
        "ADD R3, R1, R2",
        "CALL exit, R3"
    ]

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
