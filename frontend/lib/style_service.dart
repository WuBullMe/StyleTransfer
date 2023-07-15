import 'dart:convert';

import 'package:style_transfer/service.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

class StyleService implements Service {
  @override
  Future<Uint8List> submit({
    required Uint8List content,
    required Uint8List style,
    required int width,
    required int height,
    required int epochs,
    required double contentWeight,
    required double tvWeight,
    required double styleWeight,
  }) async {
    final uri = Uri.parse(
        """https://styletransferapi-1-p0532375.deta.app/test_api?image_height=$height&image_width=$width&epochs=$epochs&content_weight=$contentWeight&style_weight=$styleWeight&tv_weight=$tvWeight""");
    var headers = {'Content-Type': 'application/x-www-form-urlencoded'};
    var request = http.Request('POST', uri);
    request.bodyFields = {
      'content_image': base64.encode(content),
      'style_image': base64.encode(style),
    };
    request.headers.addAll(headers);
    http.StreamedResponse response = await request.send();
    if (response.statusCode == 200) {
      final json = jsonDecode(await response.stream.bytesToString());
      var result = json["image"] as String;
      return base64.decode(result);
    } else {
      throw Exception(response.statusCode);
    }
  }
}
