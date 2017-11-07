

int contador = 1000;
char miString[8];
bool iniciado = false;
char stringRecibido = 0x26;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(57600);
  Serial.println("Iniciando Sensor Motor DC");
  memset(miString,'\0',8);
}

void loop() {
  if(Serial.available()){
    stringRecibido = Serial.read();
    if(stringRecibido == 'I'){
      iniciado = true;
    }
    else{
      if(stringRecibido == 'T'){
        iniciado = false;
      }
    }
  }
  // put your main code here, to run repeatedly:
  /*
  Serial.print("{\"Paquete\":{\"Motor\":\"Motor Campo 001\",\"info\":{{\"voltaje\":");
  Serial.print(itoa(floor(400-contador/10),miString,10));
  Serial.print("},{\"corriente_01\":");
  Serial.print("23");
  Serial.print("},{\"temperatura\":");
  Serial.print("80");
  Serial.print("},{\"rpm\":");
  Serial.print(itoa(contador,miString,10));
  Serial.print("}}},\"fecha\":\"2017 11 02 07:55\"}");*/
  if(iniciado == true){
    delay(200);
    Serial.print("{v");
    Serial.print(itoa(floor(contador/10),miString,10));
    Serial.print(",i");
    Serial.print(itoa(300+150*cos(contador/8),miString,10));
    Serial.print(",t");
    Serial.print(itoa(200+contador/10+200*sin(contador/20),miString,10));
    Serial.print(",r");
    Serial.print(itoa(contador*contador/1000,miString,10));
    Serial.print("}");
    contador++;
  }
  if(contador>=4000){
    contador = 0;
  }

  /* rpm, temperatura, corrientes, voltajes
y necesitamos que la rasspberry la muestre en pantalla
diciendo las rpm
la temperatura el voltaje la corriente y
que ghaga grafiacas rpm vs temperatura,
rpm vs vibracion
rpm vs corriente*/
}
