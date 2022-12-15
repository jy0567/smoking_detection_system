#include "MQ7.h"

#define AVR_MAX 10 //average filter
#define level_fire 200
#define level_smoke 140

int mq7Pin = A0;
MQ7 mq7(A0, 5.0);

int redLed=12;
int greenLed=11;
int yellowLed=10;

int buzzer=2;

int freq = 150;
boolean freqFlag = true;


float get_ppm(void)
{
    float value = 0;
    
    for(int i=0; i<AVR_MAX; i++){
        value += mq7.getPPM();
        delayMicroseconds(100);
    }

    value = value/AVR_MAX;
    
    Serial.print("CO: ");
    Serial.print(value);
    Serial.println(" ppm");
    return value;
}

void setup() {
  Serial.begin(9600);

  pinMode(buzzer,OUTPUT);
  pinMode(redLed,OUTPUT);
  pinMode(greenLed,OUTPUT);
  pinMode(yellowLed,OUTPUT);
  pinMode(mq7Pin,INPUT);
}

    
void loop()
{
  float result = get_ppm();
  
  if(result >= level_fire)
  {
      digitalWrite(yellowLed,HIGH);
      digitalWrite(redLed,LOW);
      digitalWrite(greenLed,LOW);
                                  
      for(int i = 300; i <= 500; i++){
        tone(buzzer, i);
        delay(5);
      }
  
      for(int i = 500; i >= 300; i--){
        tone(buzzer, i);
        delay(3);
      }
      //noTone(buzzer);
      //delay(1000);
  }else if (result>=level_smoke && result<level_fire)
  {
      digitalWrite(redLed,HIGH);
      digitalWrite(greenLed,LOW);
      digitalWrite(yellowLed,LOW);
      
  
      for(int freq=150; freq<= 1800; freq=freq+2){
         tone(buzzer,freq,10);
      }
      for(int freq=1800; freq>= 150; freq=freq-2){
         tone(buzzer,freq,10);
      }
      //noTone(buzzer);
      //delay(1000);
  }else if(result < level_smoke)
  {
      digitalWrite(greenLed,HIGH);
      digitalWrite(redLed,LOW);
      digitalWrite(yellowLed,LOW);
      //noTone(buzzer);
      //delay(1000);
  }

  delay(1000);

}
