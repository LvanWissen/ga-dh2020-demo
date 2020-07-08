import os
import json

from typing import Union

from rdflib import Namespace, URIRef
from lxml import etree
from PIL import Image as pil_image

iiif_prezi3_context = "http://iiif.io/api/presentation/3/context.json"

nsCanvas = Namespace("https://data.goldenagents.org/datasets/dh2020/canvas/")
nsAnnotationPage = Namespace(
    "https://data.goldenagents.org/datasets/dh2020/annotationpage/")
nsAnno = Namespace("https://data.goldenagents.org/datasets/dh2020/annotation/")


def main(imagefolder: str,
         annotationfolder: str = None,
         nameslocationsfile: str = None):

    manifest = createManifest(imagefolder, annotationfolder,
                              nameslocationsfile)

    with open('iiif/manifest.json', 'w') as outfile:
        json.dump(manifest, outfile, indent=2)


def createManifest(imagefolder: str,
                   annotationfolder: str = None,
                   nameslocationsfile: str = None):

    manifest = {
        "@context": [
            "http://www.w3.org/ns/anno.jsonld",
            "http://iiif.io/api/presentation/3/context.json"
        ],
        "id":
        "https://data.goldenagents.org/datasets/dh2020/manifest/2408",
        "type":
        "Manifest",
        "label": {
            "en": ["Golden Agents DH2020 Demo"]
        },
        "summary":
        "Annotation demo, showing the benefits of cross-institutional collaboration",
        "metadata": [{
            "label": {
                "en": ["Title"]
            },
            "value": {
                "en": [
                    "Annotation demo, showing the benefits of cross-institutional collaboration"
                ]
            }
        }, {
            "label": {
                "en": ["Provenance"]
            },
            "value": {
                "en": [
                    "Amsterdam City Archives, NA 2408.",
                    "Notary Jacob de Winter (1626-1675).",
                    "Inventory dated 1648-1665."
                ]
            }
        }, {
            "label": {
                "en": ["Creator"]
            },
            "value": {
                "en": [""]
            }
        }, {
            "label": {
                "en": ["Contributor"]
            },
            "value": {
                "en": [""]
            }
        }, {
            "label": {
                "en": ["Language"]
            },
            "value": {
                "en": ["English"]
            }
        }, {
            "label": {
                "en": ["Date Statement"]
            },
            "value": {
                "en": ["2020"]
            }
        }, {
            "label": {
                "en": ["Description"]
            },
            "value": {
                "en": ["DescriptionValue"]
            }
        }, {
            "label": {
                "en": ["Collection"]
            },
            "value": {
                "en": ["Conference presentations"]
            }
        }, {
            "label": {
                "en": ["Subject"]
            },
            "value": {
                "en": [
                    "Linked Open Data", "Dutch Golden Age",
                    "Probate inventories", "Getty Provenance Index"
                ]
            }
        }, {
            "label": {
                "en": ["Other Identifier"]
            },
            "value": {
                "en": ["doi?"]
            }
        }, {
            "label": {
                "en": ["Record Created"]
            },
            "value": {
                "en": ["2020-07-20"]
            }
        }, {
            "label": {
                "en": ["Holding Institution"]
            },
            "value": {
                "en": ["Golden Agents"]
            }
        }],
        "homepage": [{
            "id": "https://www.goldenagents.org",
            "type": "Text",
            "label": {
                "en": ["View project information"]
            },
            "format": "text/html"
        }],
        "logo": [{
            "id": "assets/img/logo-golden-agents.png",
            "type": "Image"
        }],
        "thumbnail": [{
            "id": "assets/img/logo-golden-agents.png"
        }],
        "requiredStatement": {
            "label": {
                "en": ["Terms of Use"]
            },
            "value": {
                "en": [
                    "<p> <a rel=\"license\" href=\"http://creativecommons.org/licenses/by-sa/4.0/\"><img alt=\"Creative Commons License\" style=\"border-width:0\" src=\"https://licensebuttons.net/i/l/by-sa/transparent/00/00/00/88x31.png\"></a><br>This demo is developed by <a xmlns:cc=\"http://creativecommons.org/ns#\" href=\"https://www.goldenagents.org/\" property=\"cc:attributionName\" rel=\"cc:attributionURL\">Golden Agents</a> and is licensed under a <a rel=\"license\" href=\"http://creativecommons.org/licenses/by-sa/4.0/\">Creative Commons BY-SA 4.0 International License</a>. </p>"
                ]
            },
            "format": "text/html"
        },
        "behavior": ["individuals"],
        "start": {
            "id":
            "https://data.goldenagents.org/datasets/dh2020/canvas/A16098000004",
            "type": "Canvas"
        },
        "items": []
    }

    items = []

    if nameslocationsfile:
        with open(nameslocationsfile) as infile:
            nameslocationsdata = json.load(infile)
    else:
        nameslocationsdata = dict()

    for fn in sorted(os.listdir(imagefolder)):
        imagepath = os.path.join(imagefolder, fn)

        baseFilename, ext = os.path.splitext(fn)

        # HTR annotations
        if annotationfolder:
            annotationpath = os.path.join(annotationfolder,
                                          baseFilename + '.json')

            if not os.path.exists(annotationpath):

                annotationpath = None

        else:
            annotationpath = None

        # PeronNames and Locations have been selected by AAA
        nameslocations = nameslocationsdata.get(fn, [])

        canvas = getCanvas(imagepath, annotationpath, nameslocations)
        items.append(canvas)

    manifest["items"] = items

    return manifest


def getCanvas(imagepath: str,
              annotationpath: str = None,
              nameslocations: list = None,
              canvasid: str = None) -> dict:

    _, filename = os.path.split(imagepath)
    baseFilename, ext = os.path.splitext(filename)

    if canvasid is None:
        canvasid = nsCanvas.term(baseFilename)

    canvas = {
        "id":
        canvasid,
        "type":
        "Canvas",
        "label": {
            "none": [filename]
        },
        "items": [
            getAnnotationPage(target=canvasid,
                              imagepath=imagepath,
                              motivation='painting')
        ],
        "annotations": [],
        "metadata": []
    }

    annotations = []

    # index data
    if nameslocations:

        ap = getAnnotationPage(
            target=canvasid,
            baseFilename=baseFilename,
            motivation='commenting',
            annopageid=f'iiif/annotations/{baseFilename}-index.json',
            nameslocations=nameslocations,
            embedded=False)

        annotations.append(ap)

    # htr data
    if annotationpath:

        ap = getAnnotationPage(
            target=canvasid,
            motivation='supplementing',
            annopageid=f'iiif/annotations/{baseFilename}-htr.json',
            annotationpath=annotationpath,
            embedded=False)

        annotations.append(ap)

    canvas['annotations'] = annotations

    canvas['width'] = canvas['items'][0]['items'][0]['body']['width']
    canvas['height'] = canvas['items'][0]['items'][0]['body']['height']

    return canvas


def getAnnotationPage(target: Union[str, URIRef],
                      baseFilename: str = None,
                      imagepath: str = None,
                      motivation: str = 'painting',
                      annopageid: str = None,
                      annotationpath: str = None,
                      nameslocations: list = None,
                      embedded: bool = True) -> dict:

    if annopageid is None and imagepath:
        _, filename = os.path.split(imagepath)
        baseFilename, _ = os.path.splitext(filename)
        annopageid = nsAnnotationPage.term(baseFilename)
    elif annopageid is None and annotationpath:
        _, filename = os.path.split(annotationpath)
        baseFilename, _ = os.path.splitext(filename)
        annopageid = 'iiif/annotations/{basefilename}.json'
    elif annotationpath:
        _, filename = os.path.split(annotationpath)
        baseFilename, _ = os.path.splitext(filename)
    elif annotationpath is None and imagepath is None and nameslocations is None:
        return {}

    annotationPage = {
        "@context": iiif_prezi3_context,
        "id": annopageid,
        "type": "AnnotationPage",
        "items": []
    }

    if imagepath:
        annotationPage['items'] = [
            getAnnotation(target, imagepath, motivation=motivation)
        ]

    # This is for the HTR transcriptions
    if annotationpath:
        items = []

        with open(annotationpath) as infile:
            annotations = json.load(infile)

        for region in annotations['PcGts']['Page']['elements']:
            for a in region['elements']:

                coordinates = a['geometry']['coords']
                if coordinates is None:
                    continue

                targetselector = {
                    "id": target,
                    "selector": {
                        "type": "SvgSelector",
                        "value": getSVG(coordinates)
                    }
                }

                bodyValue = "\n".join([i['text'] for i in a['elements']])
                if bodyValue.strip() is "":  # not interested in empty anno
                    continue

                body = {
                    "type": "TextualBody",
                    "language": "nl",
                    "value": bodyValue
                }

                anno = getAnnotation(
                    target=targetselector,
                    motivation=motivation,
                    body=[body],
                    annoid=nsAnno.term(
                        f"{baseFilename}/{a['attributes']['id']}"))

                items.append(anno)

        annotationPage['items'] = items

    # This is data coming from the index in which Persons and Locations have been tagged
    if nameslocations:
        items = []

        for n, a in enumerate(nameslocations, 1):

            targetselector = {
                "id": target,
                "selector": {
                    "type": "FragmentSelector",
                    "value": f"xywh={a['coords']}"
                }
            }

            body = [
                {
                    "type": "TextualBody",
                    "language": "nl",
                    "value": a['label']
                },
                {
                    "type": "TextualBody",
                    "purpose": "tagging",  # for a nice tag!
                    "value": a["type"]
                }
            ]

            anno = getAnnotation(
                target=targetselector,
                motivation=motivation,
                body=body,  # already a list
                annoid=nsAnno.term(f"{baseFilename}/index{n}"))

            items.append(anno)

        annotationPage['items'] = items

    if embedded:
        return annotationPage
    else:

        with open(annopageid, 'w') as outfile:
            json.dump(annotationPage, outfile, indent=1)

        return {
            "@context": iiif_prezi3_context,
            "id": annopageid,
            "type": "AnnotationPage"
        }


def getAnnotation(target: Union[str, URIRef, dict],
                  imagepath: str = None,
                  motivation: str = 'painting',
                  body: list = None,
                  annoid: str = None) -> dict:

    if motivation == 'painting' and imagepath and type(target) != dict:

        _, filename = os.path.split(imagepath)
        baseFilename, ext = os.path.splitext(filename)

        if annoid is None:
            annoid = nsAnno.term(baseFilename)

        with pil_image.open(imagepath) as img:
            (w, h) = img.size
            height = h
            width = w

        # This is the annotation that attaches the image to the canvas
        annotation = {
            "@context": iiif_prezi3_context,
            "id": annoid,
            "type": "Annotation",
            "motivation": motivation,
            "body": {
                "id": imagepath,
                "type": "Image",
                "label": {
                    "en": [filename]
                },
                "format": "image/jpeg",
                "width": width,
                "height": height
            },
            "target": target
        }

    else:
        # But the Annotation type is also used for other commentary etc.
        annotation = {
            "@context": iiif_prezi3_context,
            "id": annoid,
            "type": "Annotation",
            "motivation": motivation,
            "body": body,
            "target": target
        }

    return annotation


def getSVG(coordinates: Union[list, tuple],
           color: str = "#66cc99",
           opacity: str = "0.08"):

    points = "M "  # start at this point
    points += " L ".join([f"{c['x']},{c['y']}" for c in coordinates
                          ])  # then move from point to point
    points += f" L {coordinates[0]['x']},{coordinates[0]['y']} Z"  # repeat the first point and close

    svg = etree.Element("svg", xmlns="http://www.w3.org/2000/svg")
    path = etree.SubElement(
        svg, "path", **{
            "fill-rule": "evenodd",
            "fill": color,
            "stroke": "#555555",
            "stroke-width": "1",
            "fill-opacity": opacity,
            "d": points
        })

    return etree.tostring(svg, encoding=str)


if __name__ == "__main__":
    main(imagefolder='images/2408/',
         annotationfolder='data/htr/2408/',
         nameslocationsfile='data/2408_nameslocations.json')
