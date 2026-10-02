#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// 1. Your home Wi-Fi credentials
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// 2. Your live Ngrok tunnel URL
const char* serverUrl = "https://unmixed-imply-retouch.ngrok-free.dev/api/sensor-alert";

// Pins
const int trigPin = 5;
const int echoPin = 18;

// Trigger threshold: distance under 20 cm triggers alert
const float TRIGGER_DISTANCE_CM = 20.0;

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  Serial.println();
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connected successfully!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

float measureDistanceCm() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000); // 30ms timeout
  if (duration == 0) return 999.0;
  return (duration * 0.0343) / 2.0;
}

void loop() {
  float distance = measureDistanceCm();

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance > 2.0 && distance < TRIGGER_DISTANCE_CM) {
    Serial.println(">>> Obstruction detected! Forwarding to Ngrok tunnel...");

    if (WiFi.status() == WL_CONNECTED) {
      WiFiClientSecure client;
      // Skip SSL certificate validation so ESP32 doesn't reject Ngrok's HTTPS cert
      client.setInsecure();

      HTTPClient http;
      if (http.begin(client, serverUrl)) {
        http.addHeader("Content-Type", "application/json");

        String payload = "{\"location\":\"kitchen sink\",\"distance_cm\":" + String(distance, 1) + "}";
        int httpCode = http.POST(payload);

        Serial.print("HTTP Response Code: ");
        Serial.println(httpCode);

        if (httpCode > 0) {
          String response = http.getString();
          Serial.println("Server returned: " + response);
        } else {
          Serial.printf("HTTP POST failed, error: %s\n", http.errorToString(httpCode).c_str());
        }

        http.end();
      } else {
        Serial.println("Unable to connect to server URL");
      }
    } else {
      Serial.println("Wi-Fi not connected!");
    }

    // Cooldown: wait 30 seconds before next trigger
    Serial.println("Cooldown active for 30 seconds...");
    delay(30000);
  } else {
    delay(2000);
  }
}