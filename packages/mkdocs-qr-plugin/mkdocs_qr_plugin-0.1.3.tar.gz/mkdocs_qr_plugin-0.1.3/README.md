# MkDocs QR Plugin

A simple plugin to create QR codes on the fly.
We use many QR codes in our manuals to explain some processes and updating the images of them regularly became cumbersome.

## Setup

Install the plugin using pip:

`pip3 install mkdocs-qr-plugin`

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - search
  - qr 
```

## Usage

To use this plugin, simply create a custom block like this

```
:::QR
title for the image
http://www.data-to.encode
:::
```

or


`````
```barcode
title: for the image
data: http://www.data-to.encode
reference: Not implemented
height: 400
width: 400
```
`````