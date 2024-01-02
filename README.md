# amazon-thumbnail-fetcher

Get the first thumbnail image of Amazon's search result.

## Requirements

For development.
- Python (See `.python-version` for version)
- rye

For deployment.
- aws cli
- npm

## Installation

Clone this repository.
```
git clone https://github.com/zaki3mymy/amazon-thumbnail-fetcher.git
cd amazon-thumbnail-fetcher
```

Install python libraries.
```
rye sync
```

## Deployment

```
cdk bootstrap --profile <your profile>
cdk deploy --profile <your profile>
```

## Usage

Specify the search word for Amazon with a query parameter `keyword`.
```
curl https://<API Gateway ID>.execute-api.ap-northeast-1.amazonaws.com/v1/thumbnail?keyword=bar | base64 -d > image.jpg
```
