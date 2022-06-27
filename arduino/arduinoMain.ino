/* Sketch for ARDUINO communication with Python.
 *  
 *  Part of master's thesis spring 2022.
 *  Anniken Semb Kvalsund
 *  Electrical Power Engineering.
 *  
 */

// Constants
const int AI[3] = {A0, A1, A2}; // Creates an array of all the analog inputs
byte noAI = (sizeof(AI)/sizeof(AI[0]));   // Finds the number of elements in AI array. To use in for loops etc

// Variables
int data1 = 0;          // Input information. Initialise to zero.
int i = 0;

bool readAI = false;
bool writeADO = false;
bool calibrateAO = false;
bool LEDcontr = false;

int AIs[10];            // For "storing" collected analogue input values
char AIstring[16];      // For storing AI values converted to string

// Write data constants and variables
const byte numChars = 16;
char receivedChars[numChars];   // an array to store the received data
byte ndx = 0;
boolean newData = false;
char analogDigital;
int channel;   // Converts the number recieved in channel number to an int
int chValConv; // Sends the char chVal to string toInt function, returned scaled and converted to int.
int outVal; // Output value to analogue PWM outputs.
bool LEDon = false; // LED controlling variable.

// Maxvalue to PWM outputs. Adjustable to ensure 5V, not more, is output at max.
int max_out_AO0 = 255; 
int max_out_AO1 = 255;
int max_out_AO2 = 255;
int max_out_AO3 = 255;

// Declare outputs
const int DO0 = 2;
const int DO1 = 4;
const int DO2 = 7;
const int DO3 = 8;

const int AO0 = 3;      // 0-10V
const int AO1 = 5;      // 0-10V
const int AO2 = 6;      // +-10V
const int AO3 = 9;      // +-10V


void setup() {
  // Setting up an initialise the serial communication
  Serial.begin(9600);       
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(DO0, OUTPUT);
  pinMode(DO1, OUTPUT);
  pinMode(DO2, OUTPUT);
  pinMode(DO3, OUTPUT);
  pinMode(AO0, OUTPUT);
  pinMode(AO1, OUTPUT);
  pinMode(AO2, OUTPUT);
  pinMode(AO3, OUTPUT);

}



void loop() {
if(Serial.available()>0){           // Return the number of bytes available on serial. if <0, = no info on serial.
  
  recvWithEndMarker();

  if(readAI == true){
    analoginputs();
    readAI = false;
  }

  if(writeADO == true){
    analogueOut();
    writeADO = false;
  }

  if(calibrateAO == true){
    calibrateAO_func();
    calibrateAO = false;
  }

  if (LEDcontr == true){
    LEDonoff();
    LEDcontr = false;
  }
  
  else{/* Do nothing*/}
  } // if serial available
} // Void loop 

//_____________________________________________________________________________________________
// Read analogue inputs

void analoginputs(){ 
  for ( i=0; i<=noAI; i++){
     AIs[i] = analogRead(AI[i]);
   } // for AI

   // Converting the analog input values to a single string with x's separating each value.
   sprintf(AIstring, "%dx%dx%d" , AIs[0],AIs[1],AIs[2]);                  
   Serial.println(AIstring);       // Writes data from AI to serial bus   
} // void analoginputs


//_____________________________________________________________________________________________
// Reads from Serial port until endChar '\n' is received.

void recvWithEndMarker() {
  char endMarker = '\n';
  char rc;
  boolean done = false;

  while (Serial.available() && !done) {
    rc = Serial.read();
    if (rc == endMarker) {
      done = true;
      newData  = true;
    }
    else {
      receivedChars[ndx++] = rc;
      if (ndx >= numChars)
        done = true;
    }
  }

  if (newData) {
    if (!parseInput()) { // if we call parseData it fails there is no need to process that data further.
      //Serial.println("String couldn't be parsed");
      newData = false;
    }
    ndx = 0;
  }
}


//_____________________________________________________________________________________________
// Splits the received string into its separate characters and stores them in globals

boolean parseInput() {
  int secondX = -1;
  String tempString;
  String chValConvtemp;
  char Buf[2];      // For converting string to char
  

  for (int i = 0; i < ndx; i++)
    //Serial.print(receivedChars[i]);
    //Serial.println();

  if (receivedChars[1] != 'x'){   // If no further values are read, ie not split by x'es
     if (receivedChars[0] == 'e'){ readAI = true;} // The readAI value is set to true, causing readAI function to run
     if (receivedChars[0] == 'h'){ LEDcontr = true; LEDon = true;}
     if (receivedChars[0] == 'i'){ LEDcontr = true; LEDon = false;}
    return false;}
  else {                          // If more than one value is transmitted

    if (receivedChars[0] == 'o' or receivedChars[0] == 'p'){ writeADO = true; analogDigital = receivedChars[0];} // Prepare to write values
    if (receivedChars[0] == 'q'){ calibrateAO = true;}   // Prepare to calibrate (using the same message system as writeADO
    
    for (int i = 3; i < ndx && secondX == -1; i++)
      if (receivedChars[i] == 'x')
        secondX = i;

    if (secondX == -1)
      return false;

    tempString = receivedChars;
    channel = tempString.substring(2, secondX).toInt();
    
    chValConvtemp = tempString.substring(secondX + 1, ndx);
    chValConvtemp.toCharArray(Buf, 2);
    chValConv = int(Buf[0]);

// Print for troubleshooting
    Serial.print("analogDigital -> ");
    Serial.println(analogDigital);
    Serial.print("channel -> ");
    Serial.println(channel);
    Serial.print("chValConv -> ");
    Serial.println(chValConv);
  }
  return true;
}

//_____________________________________________________________________________________________
// Write analogue and / or digital values

void analogueOut() { // Writes to analogue outputs

  if (newData == true) {
    // Result in an array with two elements. One A1/D2 etc and one Value/onoff

    if (analogDigital == 'o') {
      //Serial.println("Analogue");

      switch (channel) {
        case 0:
          //Serial.println("AO0");
          outVal = constrain((map(chValConv, 0, 100, 0, max_out_AO0)), 0, max_out_AO0);
          analogWrite(AO0, outVal);
          break;
        case 1:
          //Serial.println("AO1");
          outVal = constrain((map(chValConv, 0, 100, 0, max_out_AO1)), 0, max_out_AO1);
          analogWrite(AO1, outVal);
          break;
        case 2:
          //Serial.println("AO2");
          outVal = constrain((map(chValConv, 0, 100, 0, max_out_AO2)), 0, max_out_AO2);
          analogWrite(AO2, outVal);
          break;
        case 3:
          //Serial.println("AO3");
          outVal = constrain((map(chValConv, 0, 100, 0, max_out_AO3)), 0, max_out_AO3);
          analogWrite(AO3, outVal);
          break;
        default:
          //Serial.println("NaN");
          break;
      } // Switch case channel

    } // if recievedArray[0]=o

    else if (analogDigital == 'p') {
      //Serial.println("Digital");
      bool dContr = false;

      // Creating a "buffer"
      if (chValConv < 50){dContr = LOW;}
      else if (chValConv >= 50){dContr = HIGH;}
      else {dContr = LOW;}
      
      switch (channel) {
        case 0:
          //Serial.println("DO0");
          digitalWrite(DO0, dContr);
          break;
        case 1:
          //Serial.println("DO1");
          digitalWrite(DO1, dContr);
          break;
        case 2:
          //Serial.println("DO2");
          digitalWrite(DO2, dContr);
          break;
        case 3:
          //Serial.println("DO3");
          digitalWrite(DO3, dContr);
          break;
        default:
          //Serial.println("NaN");
          break;
      } // Switch case channel

    } // if recievedArray[0]=p

    else {
      //Serial.println("Channel not valid");
    } // if recievedArray[0]=p

    newData = false;
  } // if newData True
} // void analogueOut


//_____________________________________________________________________________________________

// Function for converting the recieved value 0-100 to calibration values, or reset cal. vlaues.
int calEq(int range, int measVal, int maxOut){
  int maxOut_tmp; // For storing the value temporary
  
  if (measVal == 114){  // If measVal is 114, aka reset, the max \Out is set to default 255
    maxOut_tmp = 255;
    } // if measVal 114('r')
  else { // If measVal is something else, the recieved value(measVal), scales it to measured voltage(10-11V), corrects the offset and scales the new value to out max
    maxOut_tmp = int(round(range/((range+(float(measVal)/100))/maxOut)));
  } // if measVal is not 114('r')
  
  maxOut = maxOut_tmp; 
  
  return maxOut;
  }
  
//_____________________________________________________________________________________________

void calibrateAO_func() { // Calibrate analogue PWM outs

  int range = 0; // Range of values. Set to 10 or 20, depending on output channel
  if (channel == 0 or channel == 1){range = 20;} // For AO_0 and AO_1 with -10 to +10V range
  else {range = 10;} // For AO_2 and AO_3 with 0-10V range.

 // Converted new maximum values for all four channels 
 int new_max_AO0;
 int new_max_AO1;
 int new_max_AO2;
 int new_max_AO3;

  if (newData == true) {
    switch (channel) {
      case 0:
        new_max_AO0 = calEq(range, chValConv, max_out_AO0);
        max_out_AO0 = new_max_AO0; 
        break;
      case 1:
        new_max_AO1 = calEq(range, chValConv, max_out_AO1);
        max_out_AO1 = new_max_AO1; 
        break;
      case 2:
        new_max_AO2 = calEq(range, chValConv, max_out_AO2);
        max_out_AO2 = new_max_AO2; 
        break;
      case 3:
        new_max_AO3 = calEq(range, chValConv, max_out_AO3);
        max_out_AO3 = new_max_AO3; 
        break;
      default:
        //Serial.println("NaN");
        break;
    }  // Switch case channel

    newData = false;
  } // if newData True
}


void LEDonoff(){
  if (LEDon == true) {digitalWrite(LED_BUILTIN, HIGH);}   // switch the LED on}
  //else {digitalWrite(LED_BUILTIN, LOW);}   // turn the LED off}
} // Woid LEDonoff
