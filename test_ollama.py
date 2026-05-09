import ollama

html = "<html><body><h1>Test</h1></body></html>" * 100

print("Testing review with qwen3:8b...")
try:
    r = ollama.chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": f"Review this HTML:\n{html}"}],
        options={"num_ctx": 4096}
    )
    print(f"Success: {len(r['message']['content'])} chars")
except Exception as e:
    print(f"Failed: {e}")

print("\nTesting improvement with qwen3-coder:30b...")
try:
    r = ollama.chat(
        model="qwen3-coder:30b",
        messages=[{"role": "user", "content": f"Fix this HTML:\n{html}"}],
        options={"num_ctx": 4096}
    )
    print(f"Success: {len(r['message']['content'])} chars")
except Exception as e:
    print(f"Failed: {e}")
