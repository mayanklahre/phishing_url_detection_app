from predict import predict

# Replace these example URLs with your test cases
if __name__ == "__main__":
    test_urls = [
        'https://github.com',
        'https://chat.openai.com',
        'http://192.168.0.1/login',  # example with IP in host
        'http://login-secure-account.example-login-now.com/suspicious',
        'http://very-long-subdomain.' + 'a'*80 + '.com'
    ]

    for u in test_urls:
        result = predict(u)
        print(f"URL: {u}")
        print(f" => Prediction: {result['prediction_label']} (1=phish,0=legit), score={result['prediction_score']:.2f}")
        print(" => Explanation:", result.get("explanation", "No explanation"))
        print("-"*60)
