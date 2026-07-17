# Illuminate\Http\Client\ConnectionException - Internal Server Error

cURL error 28: Operation timed out after 20001 milliseconds with 0 bytes received (see https://curl.se/libcurl/c/libcurl-errors.html) for https://sisinfo.lldikti4.id/api/restlogin/loginuser/format/json

PHP 8.3.12
Laravel 12.62.0
semar.lldikti4.id

## Stack Trace

0 - vendor/laravel/framework/src/Illuminate/Http/Client/PendingRequest.php:1810
1 - vendor/laravel/framework/src/Illuminate/Http/Client/PendingRequest.php:1086
2 - vendor/laravel/framework/src/Illuminate/Support/helpers.php:328
3 - vendor/laravel/framework/src/Illuminate/Http/Client/PendingRequest.php:1046
4 - vendor/laravel/framework/src/Illuminate/Http/Client/PendingRequest.php:890
5 - app/Http/Controllers/Auth/AuthenticatedSessionController.php:142
6 - app/Http/Controllers/Auth/AuthenticatedSessionController.php:63
7 - vendor/laravel/framework/src/Illuminate/Routing/ControllerDispatcher.php:46
8 - vendor/laravel/framework/src/Illuminate/Routing/Route.php:265
9 - vendor/laravel/framework/src/Illuminate/Routing/Route.php:211
10 - vendor/laravel/framework/src/Illuminate/Routing/Router.php:822
11 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:180
12 - vendor/laravel/framework/src/Illuminate/Auth/Middleware/RedirectIfAuthenticated.php:47
13 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
14 - app/Http/Middleware/HstsMiddleware.php:18
15 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
16 - app/Http/Middleware/LogUserActivity.php:19
17 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
18 - vendor/laravel/framework/src/Illuminate/Routing/Middleware/SubstituteBindings.php:50
19 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
20 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Middleware/VerifyCsrfToken.php:87
21 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
22 - vendor/laravel/framework/src/Illuminate/View/Middleware/ShareErrorsFromSession.php:48
23 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
24 - vendor/laravel/framework/src/Illuminate/Session/Middleware/StartSession.php:120
25 - vendor/laravel/framework/src/Illuminate/Session/Middleware/StartSession.php:63
26 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
27 - vendor/laravel/framework/src/Illuminate/Cookie/Middleware/AddQueuedCookiesToResponse.php:36
28 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
29 - vendor/laravel/framework/src/Illuminate/Cookie/Middleware/EncryptCookies.php:74
30 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
31 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:137
32 - vendor/laravel/framework/src/Illuminate/Routing/Router.php:821
33 - vendor/laravel/framework/src/Illuminate/Routing/Router.php:800
34 - vendor/laravel/framework/src/Illuminate/Routing/Router.php:764
35 - vendor/laravel/framework/src/Illuminate/Routing/Router.php:753
36 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Kernel.php:200
37 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:180
38 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Middleware/TransformsRequest.php:21
39 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Middleware/ConvertEmptyStringsToNull.php:31
40 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
41 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Middleware/TransformsRequest.php:21
42 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Middleware/TrimStrings.php:51
43 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
44 - vendor/laravel/framework/src/Illuminate/Http/Middleware/ValidatePostSize.php:27
45 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
46 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Middleware/PreventRequestsDuringMaintenance.php:109
47 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
48 - vendor/laravel/framework/src/Illuminate/Http/Middleware/HandleCors.php:61
49 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
50 - vendor/laravel/framework/src/Illuminate/Http/Middleware/TrustProxies.php:58
51 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
52 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Middleware/InvokeDeferredCallbacks.php:22
53 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
54 - vendor/laravel/framework/src/Illuminate/Http/Middleware/ValidatePathEncoding.php:26
55 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:219
56 - vendor/laravel/framework/src/Illuminate/Pipeline/Pipeline.php:137
57 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Kernel.php:175
58 - vendor/laravel/framework/src/Illuminate/Foundation/Http/Kernel.php:144
59 - vendor/laravel/framework/src/Illuminate/Foundation/Application.php:1220
60 - public/index.php:20

## Request

POST /login

## Headers

* **cookie**: XSRF-TOKEN=eyJpdiI6ImdYQXFMdDdkUzBkcEZUaml2dXp2NHc9PSIsInZhbHVlIjoiVzBLeHhQUmtYQldSdGtNNFcxZ2pZTHhXanVOdVczVnlHYkMva3JHaWRwRFlCUDAwWngyV0phZm9MQjd4WVRzaklSQ0poUHhReDVjbm53ZzdkRzdGbFhyL3JLOFd2eVNTZjVWb0ZNWFo1cjk5UHRpUkp0T1Z3VzVmYmZUd2l2dmMiLCJtYWMiOiI1NmQzYWUxNWViOWZhZTYwY2ViOTA2YWMyZjkxMzAwZDJiMzNiMjFiNmViMzlhNjBlYjUyZjNmYWRiMGVhYTVhIiwidGFnIjoiIn0%3D; semar-session=eyJpdiI6ImdGbFEvcXlpSzYzcXZnYUVKSXZhV2c9PSIsInZhbHVlIjoiVGhjUUpBTm1KOTgrcG8zayszTGNVNlhqSzlhUFlhYS9EVlJhQW42dk4weWlNTUVzcndEcmtFcnY1a3pTcG5hd2lEK2pFK2gyeGFkb1phd0lpOGxBbGkxSzBUYkMxTGVKWU5CQWdSdW92cUNZQy9VSi9HNFRZK0RRK1RKYXUxNHAiLCJtYWMiOiI4YjFiYmI1NTIyNTlhNDM4ODg0NTg1NmUyZmMxZGNkZmU1NjA2ZmUzOGE4MDUwODRkMDc5NmY0ODEyMTAzZTc2IiwidGFnIjoiIn0%3D
* **accept-language**: en-US,en;q=0.9
* **accept-encoding**: gzip, deflate, br, zstd
* **referer**: https://semar.lldikti4.id/login/sso
* **sec-fetch-dest**: document
* **sec-fetch-user**: ?1
* **sec-fetch-mode**: navigate
* **sec-fetch-site**: same-origin
* **accept**: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
* **origin**: https://semar.lldikti4.id
* **user-agent**: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
* **content-type**: application/x-www-form-urlencoded
* **upgrade-insecure-requests**: 1
* **sec-ch-ua-platform**: "Windows"
* **sec-ch-ua-mobile**: ?0
* **sec-ch-ua**: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
* **cache-control**: max-age=0
* **content-length**: 102
* **connection**: close
* **x-real-ip**: 182.9.1.248
* **x-forwarded-for**: 182.9.1.248
* **x-forwarded-proto**: https
* **x-forwarded-scheme**: https
* **host**: semar.lldikti4.id

## Route Context

controller: App\Http\Controllers\Auth\AuthenticatedSessionController@store
middleware: web, guest

## Route Parameters

No route parameter data available.

## Database Queries

* pgsql - select * from "users" where "email" = 'agungribowo' limit 1 (16.83 ms)




Illuminate\Http\Client\ConnectionException
vendor/laravel/framework/src/Illuminate/Http/Client/PendingRequest.php:1810
cURL error 28: Operation timed out after 20001 milliseconds with 0 bytes received (see https://curl.se/libcurl/c/libcurl-errors.html) for https://sisinfo.lldikti4.id/api/restlogin/loginuser/format/json

LARAVEL
12.62.0
PHP
8.3.12
UNHANDLED
CODE 0
500
POST
https://semar.lldikti4.id/login

Exception trace
5 vendor frames

Illuminate\Http\Client\PendingRequest->post()
app/Http/Controllers/Auth/AuthenticatedSessionController.php:142

137            ]);
138        }
139
140        $response = Http::asForm()
141            ->timeout(20)
142            ->post($this->getSsoLoginUrl(), [
143                'username' => $username,
144                'password' => $request->string('password')->toString(),
145            ]);
146
147        if (! $response->successful()) {
148            throw ValidationException::withMessages([
149                'username' => 'Layanan SSO sedang bermasalah. Silakan coba beberapa saat lagi.',
150            ]);
151        }
152
153        $responseData = $response->json();
154
App\Http\Controllers\Auth\AuthenticatedSessionController->handleSsoLogin()
app/Http/Controllers/Auth/AuthenticatedSessionController.php:63

7 vendor frames

Illuminate\Pipeline\Pipeline->Illuminate\Pipeline\{closure}()
app/Http/Middleware/HstsMiddleware.php:18

1 vendor frame

Illuminate\Pipeline\Pipeline->Illuminate\Pipeline\{closure}()
app/Http/Middleware/LogUserActivity.php:19

43 vendor frames

Illuminate\Foundation\Application->handleRequest()
public/index.php:20

Queries
1-1 of 1
pgsql
select * from "users" where "email" = 'agungribowo' limit 1
16.45ms
Headers
cookie
XSRF-TOKEN=eyJpdiI6IlBXL01JcytUZHQ5Ky9CVjdITSt1SlE9PSIsInZhbHVlIjoiVDRtOWNhSGlleEF1NUlGSFZ1VDdWSGJlbVlTbG1XU3o4U1pxalIyNlJMMW96WEtBZ2dVWUF0L0RYVnlXTW9PSDVKcnFwQW9nWDVLNUF4SDNBdUQvM3pZNWxuUDNMMkdHd2VNeDl3KzRNMjN5OHFMOWNRMm94YTRoVWFRZVVUZ1giLCJtYWMiOiJlNzlmZmUxMTI2YjA3Nzc0ZmVkMjNlMzU2NjI0NzI5ZDYwYTkyNTUyMjY1NThhZWVjM2FjMDA2ZGRkYmUxM2VlIiwidGFnIjoiIn0%3D; semar-session=eyJpdiI6IlVRMHdESFErdlp2eGwxR2NjT1BNeHc9PSIsInZhbHVlIjoiN3d5L0ozOWxFNE9GK1VnQmtOWVBiM2Yva3pGcTdwSkl6TGlEN3h3VTJpU2hYMDRLczRBelE3N2JpaG5MWHZSQWpuVGlucnUvRlZMTWMyWFFsaXBSV1RjS3ZKa2tjb3l5cEJVTU9XM0RudW05c3N5MjUzSVI3SHk5QmZ3Smt5R3ciLCJtYWMiOiJhOTk4NjM1ZjFlN2Y0YzQ2NWJkOWU5Yzg4ODc3ZmY5NDRlMTU4YzYxZmJjZmJkMDE4YzJkY2I0MGE3OThhYzhkIiwidGFnIjoiIn0%3D
accept-language
en-US,en;q=0.9
accept-encoding
gzip, deflate, br, zstd
referer
https://semar.lldikti4.id/login/sso
sec-fetch-dest
document
sec-fetch-user
?1
sec-fetch-mode
navigate
sec-fetch-site
same-origin
accept
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
origin
https://semar.lldikti4.id
user-agent
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36
content-type
application/x-www-form-urlencoded
upgrade-insecure-requests
1
sec-ch-ua-platform
"Windows"
sec-ch-ua-mobile
?0
sec-ch-ua
"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"
cache-control
max-age=0
content-length
102
connection
close
x-real-ip
182.9.1.248
x-forwarded-for
182.9.1.248
x-forwarded-proto
https
x-forwarded-scheme
https
host
semar.lldikti4.id
Body
{
    "_token": "CdPc3G1kaqwjEtmn8Du220cNy20bRWvnWv6R3maG",
    "login_mode": "sso",
    "username": "agungribowo",
    "password": "ciptohadi"
}
Routing
controller
App\Http\Controllers\Auth\AuthenticatedSessionController@store
middleware
web, guest
Routing parameters
// No routing parameters
