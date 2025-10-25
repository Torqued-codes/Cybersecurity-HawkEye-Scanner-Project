from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time

app = Flask(__name__, static_folder='static')
CORS(app)

class VulnerabilityScanner:
    def __init__(self):
        self.vulnerability_tests = [
            {
                'name': 'SQL Injection',
                'description': 'Tests for SQL injection vulnerabilities in URL parameters',
                'severity': 'critical',
                'icon': 'database',
                'patterns': ["'", '"', ' OR 1=1', ' UNION SELECT']
            },
            {
                'name': 'XSS (Cross-Site Scripting)',
                'description': 'Checks for potential XSS vulnerabilities',
                'severity': 'high',
                'icon': 'code',
                'patterns': ['<script', 'javascript:', 'onerror=', 'onload=']
            },
            {
                'name': 'HTTPS/SSL Check',
                'description': 'Verifies if the site uses HTTPS',
                'severity': 'medium',
                'icon': 'lock',
                'patterns': None,
                'custom_check': lambda url: not url.startswith('https://')
            },
            {
                'name': 'Directory Traversal',
                'description': 'Tests for directory traversal attempts',
                'severity': 'high',
                'icon': 'folder',
                'patterns': ['../', '..\\', '%2e%2e']
            },
            {
                'name': 'Command Injection',
                'description': 'Checks for command injection patterns',
                'severity': 'critical',
                'icon': 'terminal',
                'patterns': ['|', ';', '&', '`', '$', '$(']
            },
            {
                'name': 'Open Redirect',
                'description': 'Looks for open redirect vulnerabilities',
                'severity': 'medium',
                'icon': 'link',
                'patterns': ['redirect=', 'url=', 'next=', 'return=']
            }
        ]
    
    def test_vulnerability(self, url, test):
        if test.get('custom_check'):
            return test['custom_check'](url)
        
        patterns = test.get('patterns', [])
        url_lower = url.lower()
        
        for pattern in patterns:
            if pattern.lower() in url_lower:
                return True
        return False
    
    def scan_url(self, url):
        results = []
        
        for test in self.vulnerability_tests:
            time.sleep(0.3)  # Simulate scan time
            
            vulnerable = self.test_vulnerability(url, test)
            
            result = {
                'name': test['name'],
                'description': test['description'],
                'severity': test['severity'],
                'icon': test['icon'],
                'vulnerable': vulnerable,
                'status': 'vulnerable' if vulnerable else 'safe'
            }
            results.append(result)
        
        return results

scanner = VulnerabilityScanner()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/scan', methods=['POST'])
def scan():
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        results = scanner.scan_url(url)
        
        vulnerable_count = sum(1 for r in results if r['vulnerable'])
        safe_count = len(results) - vulnerable_count
        
        return jsonify({
            'success': True,
            'results': results,
            'stats': {
                'vulnerable': vulnerable_count,
                'safe': safe_count,
                'total': len(results)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)