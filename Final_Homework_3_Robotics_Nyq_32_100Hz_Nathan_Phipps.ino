#include <Arduino.h>

void readyState()
{
  const unsigned long transmitInterval = 1e6;        // 1 second in units of microseconds
  const char* readyMessage = "READY";
  const char* ackMessage = "ACK";
  
  char receiveBuffer[4] = {'\0'};
  size_t bytesReceived;
  
  bool ackReceived = false;
  unsigned long start = micros();
  
  while(ackReceived == false)
  {
    if(micros() - start >= transmitInterval)
    {
      Serial.println(readyMessage);
      Serial.flush();
      start = micros();
    }
    if(Serial.available() >= (int)strlen(ackMessage))
    {
      bytesReceived = Serial.readBytesUntil('\n',receiveBuffer, 3);
      if(strcmp(ackMessage,receiveBuffer) == 0)
      {
        ackReceived = true;
      }
      else{
        Serial.print("DEBUG: readyState, bytes received: ");
        Serial.println(bytesReceived);
        Serial.print("message received: ");
        Serial.println(receiveBuffer);
      }
    }
  }
}

double Sine_function(double freq){
  //Sine and noisey signal data components
  float pi = 3.14159265359; //pi
  double signal_freq_rad; //omega, 2(pi)f
  double time_a; // 1 divided by (nyquist*freq)
  float nyq; //achieves nyquist freq specs
  double recur = 0; //later used to help changing times recur and sum together
  int amplitude = 1;
  int j = 0; //used to index array and loops
  int cycles_4; // 4 cycles of samples, this was used in a while loop to ensure 4 cycles but caused issues and warnings, so scrapped
  double idealSignal; 
  double noiseSignal;

  //assigning sine and noisey components values, nyq rates used for plots = 16, 32 100
  nyq = 36; //Sampling freqeuncy is 2 or more to achieve Nyquist specs
  cycles_4 = (nyq * 4); //4 cycles, I wanted to use this to limit my while loops but arduino acted erradically when I set this as my limit, therefore all loops and arrays must be hand set depending on nyquist.
  signal_freq_rad = 2*pi*freq; //This is omega, or 2(pi)f
  time_a = 1.0/(nyq*freq); //sample period based on nyquist sampling and frequency

  //Some Components for the LP Filter
  double deltaT = 1/(nyq*freq); //could replace with time_a from above
  int fc = 400; //filter cutoff frequency 400
  int tau = 1/fc;
  double alpha = deltaT/tau;
  int k = 0;
  double x[64]; // 80 samples because 16 = nyq, 4 cycles
  double y[64]; // 80 samples because 16 = nyq, 4 cycles
  double yp = 0;
  int f = 0;
  
  //if my nyq was in the loop my serial data was weird so I had to manually adjust this value for each nyquist and cycle rate
  //for loops, for nyq of 16, 4 cycles is 64, for nyq of 8, 4 cycles is 32, for nyq = 100, 4 cycles is 400
  Serial.print("Sine Unaffected\n ");
  while(j<=((128))){ //warning recieved if end condition was nyq*4 or variable cycles_4 SO I Manually calculated each 4 cycle sample count
    //Sine Unaffected
    double some_other_freq = 1000;
    idealSignal = sin(2*pi*freq * recur) ;
    Serial.println(idealSignal); //Regular Sine
    recur += time_a; 
    j++;
  }
  
  recur = 0;
  j = 0;

  //if my nyq was in the loop my serial data was weird so I had to manually adjust this value for each nyquist and cycle rate
  //for loops, for nyq of 16, 4 cycles is 64, for nyq of 8, 4 cycles is 32, for nyq = 100, 4 cycles is 400
  Serial.println("Noisey Data");
  while(j<=((128))){ //warning recieved if end condition was nyq*4 or variable cycles_4 SO I Manually calculated each 4 cycle sample count
    //Noisey Signal
    double some_other_freq = 1000;
    idealSignal = sin(2*pi*freq * recur) ;
    noiseSignal = 1.3*cos(some_other_freq * 2*pi * recur)/random(4,6) + 0.4 * sin(some_other_freq * 2*pi * recur)/random(4,6); // recur keeps adding a sample period to each previous sample period until time reaches 4 cycles worth of samples, so if nyq = 16, then we weill observe 4 *16 samples
    x[j] = (idealSignal + noiseSignal); 
    Serial.println(x[j]); //Noisey Sine
    recur += time_a; 
    j++;
  }

  recur = 0;
  j = 0;

  //if my nyq was in the loop my serial data was weird so I had to manually adjust this value for each nyquist and cycle rate
  //for loops, for nyq of 16, 4 cycles is 64, for nyq of 8, 4 cycles is 32, for nyq = 100, 4 cycles is 400
  Serial.println("Low Pass Data");
  while(j<=((128))){ //warning recieved if end condition was nyq*4 or variable cycles_4 SO I Manually calculated each 4 cycle sample count
    //Sine Unaffected
    fc = 400;
    double some_other_freq = 1000;
    idealSignal = sin(2*pi*freq * recur) ;

    //Noisey Signal, Threw together some extra random ness in addition to suggestted noise from rubric
    noiseSignal = 1.3*cos(some_other_freq * 2*pi * recur)/random(4,6) + 0.4 * sin(some_other_freq * 2*pi * recur)/random(4,6); // recur keeps adding a sample period to each previous sample period until time reaches 4 cycles worth of samples
    x[j] = (idealSignal + noiseSignal); 
    
    //Low_Pass, I saw the python code for the a low pass in python proffessors github and repurposed it into c syntax.
    yp = yp + (time_a*fc)*(x[j]-yp); //here alpha is delatT/tau = time_a/(1/fc) = 1.0/(nyq*freq)/(1/fc)
    y[j] = yp;
    Serial.println(y[j]);
     k++;
     
    recur += time_a; // x = x+ y, so recur = recur + time_a or recur = recur + (1/nyq*freq), it advances the timeperiod going into the next cycle of sin by one sample period
    if (j == 128){
      Serial.println("Signal Values Transmitted"); //Signifies the end of transmission for the 3 signals (lp, noisey, sine), python will read this and process it for "if, name, main" loop and list processing/plotting. 
    }
    
    j++;
  }
  
}



double waitForFrequency(void)
{
  double freq;
  bool success = false;
  
  while(success == false)
  {
    while(Serial.available() < (int)sizeof(double)){
      // do nothing
    }
    
    if(Serial.readBytesUntil('\n',(char*)&freq, sizeof(freq)) == sizeof(freq)){
      Serial.println("ACK");
      success = true;
    }
    
    else{
      Serial.println("NAK");
    }
  }
  return freq;
}

// declare reset function at address 0
void(* resetFunc)(void)=0;   

int main()
{
  init();
  Serial.begin(9600);
  readyState();
  double freq = waitForFrequency();
  Serial.println(freq);
  Sine_function(freq); 
  delay(1000);
  while(1)
  {
    Sine_function(freq); // calls my signals
    delay(2000);
    resetFunc();
    freq = waitForFrequency();
  }
  return 0;
}
