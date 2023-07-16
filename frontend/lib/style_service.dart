import 'dart:convert';

import 'package:style_transfer/service.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

class StyleService implements Service {
  @override
  Future<(Uint8List, (String, String))> submit({
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
        """http://0168-172-83-13-4.ngrok-free.app/style_transfer?image_height=$height&image_width=$width&epochs=$epochs&content_weight=$contentWeight&style_weight=$styleWeight&tv_weight=$tvWeight&timeout_sec=40""");
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
      var newId = (json['content_id'].toString(), json['style_id'].toString());
      return (base64.decode(result), newId);
    } else {
      throw Exception(response.statusCode);
    }
  }

  @override
  Future<(Uint8List, (String, String))> submitLite(
      {required int width,
      required int height,
      required int epochs,
      required double contentWeight,
      required double tvWeight,
      required double styleWeight,
      required (String, String) id}) async {
    
    final uri = Uri.parse(
        """http://0168-172-83-13-4.ngrok-free.app/change_weights?content_id=${id.$1}&style_id=${id.$2}&image_height=$height&image_width=$width&epochs=$epochs&content_weight=$contentWeight&style_weight=$styleWeight&tv_weight=$tvWeight&timeout_sec=40""");
    var headers = {'Content-Type': 'application/x-www-form-urlencoded'};
    var request = http.Request('POST', uri);
    request.headers.addAll(headers);
    http.StreamedResponse response = await request.send();
    if (response.statusCode == 200) {
      final json = jsonDecode(await response.stream.bytesToString());
      var result = json["image"] as String;  
      var newId = (json['content_id'].toString(), json['style_id'].toString());
      return (base64.decode(result), newId);
    } else {
      throw Exception(response.statusCode);
    }
  }
}
