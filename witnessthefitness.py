from fire import FireProx
import datetime
import argparse
import json


def main(args):

    if args.command == "create":
        if args.urls == None or args.outfile == None:
            print("Eyewitness file creation requires url and outfile inputs")
            return
    elif args.command == "delete":
        if args.api_id == None:
            print("Delete command requires API ID input")
            return
    else:
        pass

    if args.config != None:
        print("[+] Loading AWS configuration details from file: {}".format(args.config))
        aws_dict = json.loads(open(args.config).read())
        access_key = aws_dict['access_key']
        secret_access_key = aws_dict['secret_access_key']
    else:
        access_key = args.access_key
        secret_access_key = args.secret_access_key

    if access_key == None or secret_access_key == None:
        print("Please input access key and secret access key for AWS authentication")
        return


    if args.command != "create":
        fp_command(access_key, secret_access_key, "", "", args.region, args.command, args.api_id)
        return

    version_date = f'{datetime.datetime.now():%Y-%m-%dT%XZ}'
    title = 'fireprox_wtf'

    template = '''
    {
      "swagger": "2.0",
      "info": {
        "version": "{{version_date}}",
        "title": "{{title}}"
      },
      "basePath": "/",
      "schemes": [
        "https"
      ],
      "paths": {
        "/": {
          "get": {
            "parameters": [
              {
                "name": "proxy",
                "in": "path",
                "required": true,
                "type": "string"
              },
              {
                "name": "X-My-X-Forwarded-For",
                "in": "header",
                "required": false,
                "type": "string"
              }
            ],
            "responses": {},
            "x-amazon-apigateway-integration": {
              "uri": "https://github.com/knavesec/EyeWitnessTheFitness",
              "responses": {
                "default": {
                  "statusCode": "200"
                }
              },
              "requestParameters": {
                "integration.request.path.proxy": "method.request.path.proxy",
                "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For"
              },
              "passthroughBehavior": "when_no_match",
              "httpMethod": "ANY",
              "cacheNamespace": "irx7tm",
              "cacheKeyParameters": [
                "method.request.path.proxy"
              ],
              "type": "http_proxy"
            }
          }
        }

        {{template_additions}}

      }
    }
    '''


    template_add = '''
        "/{{url}}/": {
          "x-amazon-apigateway-any-method": {
            "produces": [
              "application/json"
            ],
            "parameters": [
              {
                "name": "proxy",
                "in": "path",
                "required": true,
                "type": "string"
              },
              {
                "name": "X-My-X-Forwarded-For",
                "in": "header",
                "required": false,
                "type": "string"
              }
            ],
            "responses": {},
            "x-amazon-apigateway-integration": {
              "uri": "{{url_full}}/{proxy}",
              "responses": {
                "default": {
                  "statusCode": "200"
                }
              },
              "requestParameters": {
                "integration.request.path.proxy": "method.request.path.proxy",
                "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For"
              },
              "passthroughBehavior": "when_no_match",
              "httpMethod": "ANY",
              "cacheNamespace": "irx7tm",
              "cacheKeyParameters": [
                "method.request.path.proxy"
              ],
              "type": "http_proxy"
            }
          }
        },
        "/{{url}}/{proxy+}": {
          "x-amazon-apigateway-any-method": {
            "produces": [
              "application/json"
            ],
            "parameters": [
              {
                "name": "proxy",
                "in": "path",
                "required": true,
                "type": "string"
              },
              {
                "name": "X-My-X-Forwarded-For",
                "in": "header",
                "required": false,
                "type": "string"
              }
            ],
            "responses": {},
            "x-amazon-apigateway-integration": {
              "uri": "{{url_full}}/{proxy}",
              "responses": {
                "default": {
                  "statusCode": "200"
                }
              },
              "requestParameters": {
                "integration.request.path.proxy": "method.request.path.proxy",
                "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For"
              },
              "passthroughBehavior": "when_no_match",
              "httpMethod": "ANY",
              "cacheNamespace": "irx7tm",
              "cacheKeyParameters": [
                "method.request.path.proxy"
              ],
              "type": "http_proxy"
            }
          }
        }
    '''


    urls = open(args.urls,'r').readlines()

    print("[+] {} URLs read from file: {}".format(len(urls),args.urls))

    template_additions = ''
    short_urls = []

    print("[+] Generating template")
    for url in urls:
        url_full = url.strip()
        url_split = url_full.split("/")[2]
        short_urls.append(url_split)

        template_addition = template_add
        template_addition = template_addition.replace("{{url}}", url_split)
        template_addition = template_addition.replace("{{url_full}}", url_full)

        template_additions = template_additions + ',' + template_addition

    template = template.replace("{{template_additions}}", template_additions)
    template = template.replace("{{title}}", title)
    template = template.replace("{{version_date}}", version_date)

    print("[+] Creating API")
    vars = create_api(access_key, secret_access_key, "", "", args.region, template)

    print("[+] API Created: {}".format(vars['proxy_url']))
    print("[+] Writing EyeWitness web URL file at {}".format(args.outfile))

    f = open(args.outfile,'a')
    for url in short_urls:
        f.write(vars['proxy_url'] + url + '/')
        f.write('\n')
    f.close()

    print("[+] Done")
    print("[+] Now run: python3 Eyewitness.py --web -f {} [other inputs]".format(args.outfile))


def get_fireprox_args(access_key, secret_access_key, profile_name, session_token, command, region):

	args = {}
	args["access_key"] = access_key
	args["secret_access_key"] = secret_access_key
	args["url"] = ""
	args["command"] = command
	args["region"] = region
	args["api_id"] = ""
	args["profile_name"] = profile_name
	args["session_token"] = session_token

	help_str = "Fireprox errored and catches so much that there is no detail. Common error is system time being off by 5+ minutes"

	return args, help_str


def create_api(access_key, secret_access_key, profile_name, session_token, region, template):

	args, help_str = get_fireprox_args(access_key, secret_access_key, profile_name, session_token, "create", region)
	fp = FireProx(args, help_str)
	resource_id, proxy_url = fp.create_api(template)
	return { "api_gateway_id" : resource_id, "proxy_url" : proxy_url }


def fp_command(access_key, secret_access_key, profile_name, session_token, region, command, api_id):

    args, help_str = get_fireprox_args(access_key, secret_access_key, profile_name, session_token, command, region)
    fp = FireProx(args, help_str)
    if command == "list":
        fp.list_api()
    else:
        fp.delete_api(api_id)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--urls', type=str, default=None, required=False, help="List of target HTTP/S hosts (must have http:// or https:// prepended on every line)")
    parser.add_argument('-o', '--outfile', type=str, default=None, required=False, help="Desired output file")
    parser.add_argument('--region', type=str, default="us-east-2", required=True, help="Region to create API in (default: us-east-2)")
    parser.add_argument('--command', type=str, default="create", required=False, choices=["list", "delete", "create"], help="FireProx command input other than default list create [list, delete]")
    parser.add_argument('--api_id', type=str, default=None, required=False, help="API ID, used to delete an API")
    parser.add_argument('--access_key', type=str, default=None, help='AWS Access Key')
    parser.add_argument('--secret_access_key', type=str, default=None, help='AWS Secret Access Key')
    parser.add_argument('--config', type=str, default=None, help='Authenticate to AWS using config file aws.config')
    args = parser.parse_args()

    main(args)
