from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to the running application
    page.goto("http://localhost:5174/")

    # Wait for the "Model Management" card to be visible, which indicates the page is loading
    expect(page.get_by_text("Model Management")).to_be_visible(timeout=15000)

    # Wait for the "Bot Control" card to be visible
    expect(page.get_by_text("Bot Control")).to_be_visible()

    # Wait for the content within the cards to be populated
    # This confirms the useEffect hooks have run
    expect(page.get_by_text("Last Trained:")).to_be_visible()
    expect(page.get_by_text("INACTIVE")).to_be_visible()

    # Take a screenshot of the entire page
    page.screenshot(path="jules-scratch/verification/verification.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)