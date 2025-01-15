from burphttp import burphttp

request_content = open('curlcommand.txt').read()

bq = burphttp()
print(bq.parse_curl(request_content))
# bq.send_request()
# bq.save_response_body("response.http")
