# EyeWitnessTheFitness #

External recon got ya down? That scan prevention system preventing you from enumerating web pages? Well look no further, I have the tool for you

Generate one FireProx API to be used for all your EyeWitness targets, making your enumeration both opsec-friendly and convenient.

**Note:** Your IP address will be disclosed in the `X-Forwarded-For` header as with the OG FireProx. The compatibility is there to be spoofed with the `X-My-X-Forwarded-For` header, but that has to be done via modding eyewitness

**Second Note:** Use a normal FireProx API for anything outside of Eyewitness enum, actual testing on this API will likely result in the website not acting properly due to API URI issues

**Third Note:** Maximum number of URLs per API endpoint is 150, so if you have more chop them up into 150 url bits and create an endpoint for each

## Usage ##

Start off with a list of Eyewitness targets in a file, make sure they all have http:// or https:// prepended to the URL. Run the script specifying what AWS region you want it in, then it will output your new Eyewitness target file.

```
root@echo:/opt/EyeWitnessTheFitness# python3 witnessthefitness.py {config or access/secret access keys} --region us-east-2 -u urls.txt -o eyewitnessout.txt
[+] 3 URLs read from file: urls.txt
[+] Generating template
[+] Creating API
[+] API Created: https://{api id}.execute-api.us-east-2.amazonaws.com/fireprox/
[+] Writing EyeWitness web URL file at eyewitnessout.txt
[+] Done
[+] Now run: python3 Eyewitness.py --web -f eyewitnessout.txt [other inputs]
```

```
Example eyewitnessout.txt
https://{api id}.execute-api.us-east-2.amazonaws.com/fireprox/nmap.org/
https://{api id}.execute-api.us-east-2.amazonaws.com/fireprox/apache.org/
https://{api id}.execute-api.us-east-2.amazonaws.com/fireprox/www.google.com/
```

Then you just run Eyewitness with your new file. Each request will have a different IP address which is what most IPS systems block by.

```
python3 Eyewitness.py --web -f eyewitnessout.txt
```

### Contact ###

Feel free to drop me a line

[twitter](https://twitter.com/knavesec) - \@knavesec

[Inspiration](https://www.youtube.com/watch?v=_PP1AK1Aqis&t=92s) - \#RedTeamFit
