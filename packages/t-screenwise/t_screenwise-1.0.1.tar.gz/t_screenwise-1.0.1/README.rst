Screenwise Framework
===================

A Python framework for screen element detection and interaction using computer vision and machine learning.

Overview
--------
Screenwise provides automated detection and interaction with UI elements through:

* Screenshot capture and analysis
* ML-based element detection 
* Coordinate-based interaction
* OCR capabilities
* Debug and capture modes
* Cross-platform support

Installation
-----------
.. code-block:: bash

    pip install screenwise

Basic Usage
----------

Initialize Framework
~~~~~~~~~~~~~~~~~~
.. code-block:: python

    from t_screenwise.screenwise import Framework

    # Initialize with default settings
    framework = Framework()

    # Initialize with custom settings
    framework = Framework(
        mode="CAPTURE",
        model_path="path/to/model.pth",
        labels="path/to/labels.json",
        device="cpu"
    )

Detect Elements
~~~~~~~~~~~~~~
.. code-block:: python

    # Get all detected elements
    elements = framework.get()

    # Filter for specific element types
    buttons = framework.get(filter=["button"])
    text = framework.get(filter=["text"])

Interact with Elements
~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    # Click element
    element.click()

    # Click at specific position
    element.click(coords="up_right")

    # Type text
    element.send_keys("Hello World")

    # Click and type
    element.click_and_send_keys("Hello World")

Process OCR Elements
~~~~~~~~~~~~~~~~~~
.. code-block:: python

    framework = Framework()
    results = framework.get(image="path/to/image.png", process_ocr=True)

    # Work with both types of elements
    for element in results:
        if isinstance(element, OCRElement):
            print(f"OCR Text: {element.text} (Confidence: {element.confidence})")
        else:
            print(f"Box Label: {element.label}")

Features
--------

Screen Elements
~~~~~~~~~~~~~~
* Coordinate-based positioning
* Margin calculations
* Drawing capabilities

Mouse and keyboard interaction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Debug visualization

OCR Elements
~~~~~~~~~~~
* Text content extraction
* Confidence scoring
* Spatial relationship analysis
* Text-based element search

Operating Modes
~~~~~~~~~~~~~
* CAPTURE: Live interaction with screen elements
* DEBUG: Visualization and testing without actual interaction

Configuration
------------

Labels
~~~~~~
Labels are defined in a JSON file mapping element types to numeric IDs:

.. code-block:: json

    {
        "button": 1,
        "text": 2,
        "input": 3
        // etc...
    }

Model
~~~~~
Supports custom trained object detection models:

* Default model trained for common UI elements
* Configurable confidence thresholds

Contributing
-----------
1. Clone the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request