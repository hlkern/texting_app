#include <ArduinoJson.h>

String inputString = ""; // Gelen veriyi saklamak için bir string
bool stringComplete = false; // Mesajın tamamlanıp tamamlanmadığını kontrol eder

void setup() {
  Serial.begin(9600); // Baud rate ayarları
  inputString.reserve(200); // Veriyi saklamak için yeterli alan ayırır
}

void loop() {
   // Eğer bir mesaj tam olarak alınmışsa
  if (stringComplete) {
    // Başlangıç ve bitiş karakterlerini kontrol et
    int startIdx = inputString.indexOf('<');
    int endIdx = inputString.indexOf('>');
    if (startIdx >= 0 && endIdx > startIdx) {
      String jsonString = inputString.substring(startIdx + 1, endIdx);
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, jsonString);
      
      // Eğer JSON verisi doğruysa
      if (!error) {
        const char* name = doc["name"];
        int x = doc["x"];
        int y = doc["y"];
        
        Serial.print("Name: ");
        Serial.println(name);
        Serial.print("X: ");
        Serial.println(x);
        Serial.print("Y: ");
        Serial.println(y);
      } else {
        Serial.println("JSON parsing failed!");
      }
    } else {
      Serial.println("Invalid message format!");
    }
    
    // String'i temizle ve yeni veri için hazırla
    inputString = "";
    stringComplete = false;
  }
  // JSON verisi oluşturma
  StaticJsonDocument<200> doc;
  doc["name"] = "test";
  doc["x"] = 150;
  doc["y"] = 200;

  // JSON verisini stringe dönüştürme
  char output[128];
  serializeJson(doc, output);

  // Veriyi başlangıç ve bitiş karakterleri ile gönderme
  Serial.print("{");
  Serial.print(output);
  Serial.println("}");

  delay(1000); // 1 saniye bekle
}
// Seri porttan veri geldiğinde çağrılır
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    
    // Eğer bitiş karakterine ulaşıldıysa mesaj tamamlanmıştır
    if (inChar == '>') {
      stringComplete = true;
    }
  }
}
