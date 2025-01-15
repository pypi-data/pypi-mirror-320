import asyncio
from pyppeteer import launch


async def run_python_with_pyodide(code_string):
    # Launch the browser in headless mode
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Load Pyodide via CDN
    await page.goto('data:text/html,<script src="https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js"></script>')

    # Evaluate Python code in Pyodide, capturing stdout
    result = await page.evaluate(f"""
        async () => {{
            const pyodide = await loadPyodide();
            try {{
                let output = "";
                const captureOutput = (text) => {{ output += text + "\\n"; }};

                // Redirect stdout in Pyodide
                pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
                `);

                // Run the provided code
                pyodide.runPython(`{code_string}`);

                // Retrieve stdout
                const std_output = pyodide.runPython("sys.stdout.getvalue()");
                return {{ success: true, output: std_output }};
            }} catch (error) {{
                return {{ success: false, error: error.toString() }};
            }}
        }}
    """)

    # Close the browser instance
    await browser.close()
    return result


# Example usage
async def main():
    code = """
sentence = "how many vowels are in this exact sentence?"
vowels = "aeiouAEIOU"
count = 0
for char in sentence:
    if char in vowels:
        count += 1
print(f"Vowel Count: {count}")

"""
    # Run the code in Pyodide and get the result
    result = await run_python_with_pyodide(code)
    if result['success']:
        print("Output from Pyodide:")
        print(result['output'])
    else:
        print("Error in Pyodide:", result['error'])


if __name__ == "__main__":
    asyncio.run(main())