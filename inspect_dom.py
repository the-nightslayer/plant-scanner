from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('http://localhost:8501')
        page.wait_for_selector('h1')
        page.wait_for_timeout(3000) # give 3 seconds just in case
        
        script = """
        () => {
            let result = '';
            function walk(node, depth) {
                if(node.nodeType !== 1) return;
                const style = window.getComputedStyle(node);
                const rect = node.getBoundingClientRect();
                
                // only print nodes with actual size, ignore 0 height elements
                if (rect.width > 0 && rect.height > 0) {
                    let info = '<' + node.tagName.toLowerCase();
                    if(node.getAttribute('data-testid')) info += ' data-testid="' + node.getAttribute('data-testid') + '"';
                    if(node.className && typeof node.className === 'string') info += ' class="' + node.className.substring(0,40) + '..."';
                    if(node.textContent && node.children.length === 0) {
                        info += ' text="' + node.textContent.substring(0, 30).trim() + '"';
                    }
                    
                    info += '> [' + Math.round(rect.width) + 'x' + Math.round(rect.height) + ']';
                    
                    // IF IT HAS ANY BACKGROUND (not transparent/black) we specifically mark it
                    if (style.backgroundColor !== 'rgba(0, 0, 0, 0)' && style.backgroundColor !== 'transparent') {
                        info += ' BG_COLOR=' + style.backgroundColor;
                    }
                    if (style.backgroundColor === 'rgb(255, 255, 255)' || style.backgroundColor.startsWith('rgba(255, 255, 255')) {
                        info += ' !!! WHITE BACKGROUND !!!';
                    }
                    
                    result += '  '.repeat(depth) + info + '\\n';
                }
                
                for(let child of node.children) {
                    walk(child, depth + 1);
                }
            }
            
            walk(document.body, 0);
            return result;
        }
        """
        html = page.evaluate(script)
        
        with open('/tmp/dom_dump.txt', 'w', encoding='utf-8') as f:
            f.write(html)
            
        print("DOM dumped successfully to /tmp/dom_dump.txt")
        browser.close()

if __name__ == '__main__':
    run()
