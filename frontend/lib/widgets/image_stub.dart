import 'dart:typed_data';

import 'package:flutter/material.dart';

class ImageStub extends StatelessWidget {
  const ImageStub({
    super.key,
    this.imageBytes,
    this.width = 250,
    this.height = 250,
    this.text = 'No image chosen',
    this.fill = false,
  });

  final Uint8List? imageBytes;
  final double width;
  final double height;
  final String text;
  final bool fill;

  @override
  Widget build(BuildContext context) {
    // return ConstrainedBox(
      // constraints: BoxConstraints(
      //   maxHeight: height,
      //   maxWidth: width,
      // ),
      return Container(
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey),
        ),
        height: height,
        width: width,
        child: imageBytes == null
            ? Center(
                child: Text(text),
              )
            : Image.memory(
                imageBytes!,
                // fit: BoxFit.contain,
              ),
      // ),
    );
  }
}
