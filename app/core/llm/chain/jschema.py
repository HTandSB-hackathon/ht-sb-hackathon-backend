SCHEMA_CNVERSATION_ANALYSIS = '''{
  "type": "object",
  "required": ["matched_words", "total_matched_count"],
  "properties": {
    "matched_words": {
      "type": "array",
      "maxItems": 5,
      "items": {
        "type": "object",
        "required": ["word", "type", "reason", "count_in_message"],
        "properties": {
          "word": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
          },
          "type": {
            "type": "string",
            "enum": ["方言", "地名", "特産品", "観光地", "文化"]
          },
          "reason": {
            "type": "string",
            "minLength": 1,
            "maxLength": 300
          },
          "count_in_message": {
            "type": "integer",
            "minimum": 1
          }
        }
      }
    },
    "total_matched_count": {
      "type": "integer",
      "minimum": 0
    }
  }
}'''

SCHEMA_POSITIVE_ANALYSIS = '''"type": "object",
  "required": ["sentiment", "confidence", "reason"],
  "properties": {
    "sentiment": {
      "type": "string",
      "enum": ["positive", "neutral", "negative"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "reason": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500
    }
}'''