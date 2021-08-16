#include <Arduino.h>
#include "configs.h"
#include <WiFi.h>


#define RESET 0 
#define RESTING 1
#define SLOWDOWN 2
#define STOPPED 3
#define BUZZER 4
#define MOVING 5
#define OBSTACLE 6
#define EMERGENCY_STOP 7
#define FORWARD 8
#define REVERSE 9


#define WIFI_DISCONNECTED 0
#define WIFI_CONNECTED 1
#define WIFI_RECONNECTING 2

#define SOCKET_DISCONNECTED 0
#define SOCKET_RECONNECTING 1
#define SOCKET_CONNECTED 2

int previous_rover_state = RESET;
int current_rover_state = RESET;
int rover_prev_state = RESET;
int previous_sent_state=RESET;
int wifi_current_state = WIFI_DISCONNECTED;
int current_socket_state=SOCKET_DISCONNECTED;

bool flag_obstacle =false;

unsigned long server_ack_timer_0 = 0;
unsigned long server_ack_timer_now = 0;

unsigned long wait_timer_0 = 0;
unsigned long reconnecting_timer_0 = 0 ;
unsigned long last_state_update = 0;
unsigned long last_emergency_update = 0;
unsigned long last_obstacle_msg_send  = 0;
unsigned long obstacle_removed_timer0 = 0;

WiFiClient espclient;

int wifi_state_machine();
int state_machine_rover();
int socket_state_machine();
String getMessage();
int sendMessage(String);
int sendState(int state);

void setup() {
  // put your setup code here, to run once:
    Serial.begin(115200);
    WiFi.begin(WIFI_SSID,WIFI_PSD);
    pinMode(FORWARD_PIN,OUTPUT);
    pinMode(REVERSE_PIN,OUTPUT);
    pinMode(SLOWDOWN_PIN,OUTPUT);
    pinMode(BUZZER_PIN,OUTPUT);
    pinMode(OBSTACLE_SENSOR_B_PIN,INPUT);
    pinMode(OBSTACLE_SENSOR_F_PIN,INPUT);
    pinMode(LIMIT_SWITCH_B_PIN,INPUT);
    pinMode(LIMIT_SWITCH_F_PIN,INPUT);
    digitalWrite(FORWARD_PIN,LOW);
    digitalWrite(REVERSE_PIN,LOW);
    digitalWrite(SLOWDOWN_PIN,LOW);
    digitalWrite(BUZZER_PIN,LOW);


    while (WiFi.status()!= WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Wifi Connected");
    wifi_current_state = WIFI_CONNECTED;


}

void loop() {
  // put your main code here, to run repeatedly:
    if(wifi_state_machine()==WIFI_CONNECTED){
        if(socket_state_machine()==SOCKET_CONNECTED){
            state_machine_rover();
        }
    }
}


int state_machine_rover(){
    if(previous_sent_state!=current_rover_state || millis()-last_state_update>2000){
        sendState(current_rover_state);
        last_state_update = millis();
        previous_sent_state = current_rover_state;
    }
    // read sensor values
    // set states if triggered
    
    // Check if sensors read anythingA

    int sensor_state = (digitalRead(OBSTACLE_SENSOR_B_PIN)&&
                        digitalRead(LIMIT_SWITCH_B_PIN)&&
                        digitalRead(OBSTACLE_SENSOR_F_PIN)&&
                        digitalRead(LIMIT_SWITCH_F_PIN));

    if (sensor_state == 0){
        if (current_rover_state != OBSTACLE){ 
            previous_rover_state = current_rover_state;
            current_rover_state = OBSTACLE;
            flag_obstacle = true;
        }
    }else if(sensor_state ==1 && flag_obstacle == true  ){
        flag_obstacle = false;
        obstacle_removed_timer0 = millis();
    }

    // check any message arrived
    String msgIn = getMessage();
    int msglength = msgIn.length();
    if(msglength!=0){
        Serial.println(msgIn);
    }

    if (msgIn.compareTo("FORWARD")==0){
        Serial.println("Going forward");
        sendMessage("FORWARD|ACK");
        current_rover_state = FORWARD;
    }

    if (msgIn.compareTo("REVERSE")==0){
        Serial.println("Going Reverse");
        sendMessage("REVERSE|ACK");
        current_rover_state =  REVERSE;
    }

    if (msgIn.compareTo("SLOWDOWN")==0){
        Serial.println("Slowdown");
        sendMessage("SLOWDOWN|ACK");
        current_rover_state = SLOWDOWN ;
    }
    if (msgIn.compareTo("RESTING")==0){
        Serial.println("Slowdown");
        sendMessage("RESTING|ACK");
        current_rover_state = RESTING ;
    }

    if (msgIn.compareTo("STOP")==0){
        Serial.println("STOP");
        sendMessage("STOP|ACK");
        current_rover_state = STOPPED;
        wait_timer_0 = millis();
    }

    switch (current_rover_state)
    {
    case  FORWARD:
        digitalWrite(REVERSE_PIN, LOW);
        digitalWrite(BUZZER_PIN,LOW);
        digitalWrite(SLOWDOWN_PIN,LOW);
        digitalWrite(FORWARD_PIN, HIGH);
        break;
    case  REVERSE:
        digitalWrite(REVERSE_PIN, HIGH);
        digitalWrite(BUZZER_PIN,LOW);
        digitalWrite(SLOWDOWN_PIN,LOW);
        digitalWrite(FORWARD_PIN, LOW);
        break;
    case  STOPPED:
        digitalWrite(REVERSE_PIN, LOW);
        digitalWrite(BUZZER_PIN,LOW);
        digitalWrite(SLOWDOWN_PIN,LOW);
        digitalWrite(FORWARD_PIN, LOW);
        if (millis()-wait_timer_0 > 30000){
            current_rover_state = BUZZER;
        }
        break;
    case BUZZER:
        digitalWrite(BUZZER_PIN,HIGH);
        digitalWrite(REVERSE_PIN, LOW);
        digitalWrite(SLOWDOWN_PIN,LOW);
        digitalWrite(FORWARD_PIN, LOW);
        Serial.println("BUZZER");
    case  SLOWDOWN:
        digitalWrite(REVERSE_PIN, LOW);
        digitalWrite(BUZZER_PIN,LOW);
        digitalWrite(SLOWDOWN_PIN,HIGH);
        digitalWrite(FORWARD_PIN, LOW);
        /* code */
        break;
    
    case OBSTACLE:
        digitalWrite(BUZZER_PIN,HIGH);
        digitalWrite(REVERSE_PIN, LOW);
        digitalWrite(SLOWDOWN_PIN,LOW);
        digitalWrite(FORWARD_PIN, LOW); 
        if (millis() - obstacle_removed_timer0 > 3000 && flag_obstacle == false){
            current_rover_state = previous_rover_state;

        }

    case RESTING:
        digitalWrite(BUZZER_PIN,LOW);
        digitalWrite(FORWARD_PIN,LOW);
        digitalWrite(REVERSE_PIN,LOW);
        digitalWrite(SLOWDOWN_PIN,LOW);
        break;

    case EMERGENCY_STOP:
        digitalWrite(BUZZER_PIN,HIGH);
        digitalWrite(FORWARD_PIN,LOW);
        digitalWrite(REVERSE_PIN,LOW);
        digitalWrite(SLOWDOWN_PIN,LOW);
        break;


    default:
        break;
    }

    

    
//     switch (current_rover_state)
//     {
        
//         case RESET:
//             previous_rover_state = current_rover_state;
//             current_rover_state = RESTING;
//             break;


//         case RESTING:
//         case MOVING:
//             digitalWrite(SLOWDOWN_PIN,LOW);
//             Serial.println("Here");
//             Serial.println(msgIn);
//             if(msgIn.compareTo("ROVER|FORWARD")==0){
//                 sendMessage("FORWARD|ACK");
//                 digitalWrite(REVERSE_PIN,LOW);
//                 digitalWrite(FORWARD_PIN,HIGH);
//             }
//             if(msgIn.compareTo("ROVER|REVERSE")==0){
//                 sendMessage("REVERSE|ACK");
//                 digitalWrite(FORWARD_PIN,LOW);
//                 digitalWrite(REVERSE_PIN,HIGH);
//             } 
//             if(msgIn.compareTo("ROVER|SLOWDOWN")==0){
//                 sendMessage("SLOWDOWN|ACK");
//                 previous_rover_state = current_rover_state;
//                 current_rover_state=SLOWDOWN;

//             }
//             break;

//         case SLOWDOWN:
//             // Slow down the rover
//             digitalWrite(SLOWDOWN_PIN,HIGH);
//             // Check for message stop the rover and move to next state
//             if (msgIn.compareTo("ROVER|STOP")==0){
//                 digitalWrite(FORWARD_PIN,LOW);
//                 digitalWrite(REVERSE_PIN,LOW);
//                 digitalWrite(SLOWDOWN_PIN,LOW);

//                 previous_rover_state = current_rover_state;
//                 current_rover_state = STOPPED;
//                 sendMessage("ROVER|STOPPED");
//                 wait_timer_0 = millis();

//             }
            
//             break;


//         case STOPPED:
//             if(msgIn.compareTo("ROVER|START")==0){
//                 sendMessage("START|ACK");
//                 previous_rover_state = current_rover_state;
//                 current_socket_state = MOVING;
//                 break;
//             }
//             if(msgIn.compareTo("ROVER|FORWARD")==0){
//                 sendMessage("FORWARD|ACK");
//                 digitalWrite(REVERSE_PIN,LOW);
//                 digitalWrite(FORWARD_PIN,HIGH);

//                 previous_rover_state = current_rover_state;
//                 current_socket_state = MOVING;
//             }
//             if(msgIn.compareTo("ROVER|REVERSE")==0){
//                 sendMessage("REVERSE|ACK");
//                 digitalWrite(FORWARD_PIN,LOW);
//                 digitalWrite(REVERSE_PIN,HIGH);
//                 previous_rover_state = current_rover_state;
//                 current_socket_state = MOVING;
//             }
            
//             if( millis() - wait_timer_0 > 30000){
//                 sendMessage("ROVER|BUZZING");
//                 previous_rover_state = current_rover_state;
//                 current_rover_state = BUZZER;

//             }
//             break;

//         case BUZZER:
//             digitalWrite(BUZZER_PIN,HIGH);
//             if(msgIn.compareTo("ROVER|START")==0){
//                 sendMessage("START|ACK");
//                 digitalWrite(BUZZER_PIN,LOW);
//                 previous_rover_state = current_rover_state;
//                 current_socket_state = MOVING;
//                 break;
//             }
//             if(msgIn.compareTo("ROVER|FORWARD")==0){
//                 sendMessage("FORWARD|ACK");
//                 digitalWrite(REVERSE_PIN,LOW);
//                 digitalWrite(FORWARD_PIN,HIGH);

//                 previous_rover_state = current_rover_state;
//                 current_socket_state = MOVING;
//             }
//             if(msgIn.compareTo("ROVER|REVERSE")==0){
//                 sendMessage("REVERSE|ACK");
//                 digitalWrite(FORWARD_PIN,LOW);
//                 digitalWrite(REVERSE_PIN,HIGH);
//                 previous_rover_state = current_rover_state;
//                 current_socket_state = MOVING;
//             }
//             //if(msg == go )
//             //digitalWrtie(BUZZER_PIN,LOW)
//             //previous_rover_state = current_rover_state;
//             //current_rover_state = MOVING; 

//             break;


//         case EMERGENCY_STOP:
//             digitalWrite(FORWARD_PIN,LOW);
//             digitalWrite(REVERSE_PIN,LOW);
//             if(millis()-last_emergency_update > 1000){

//                 sendMessage("EMERGENCY|STOPPED");
//                 last_emergency_update = millis(); 
//             }

//             break;
        
//         case OBSTACLE:
//             // check if one second passed and check the pins if none are engaged go back to previous state
            
//             digitalWrite(FORWARD_PIN,LOW);
//             digitalWrite(REVERSE_PIN,LOW);
//             digitalWrite(BUZZER_PIN,HIGH);
//             if(millis()-last_obstacle_msg_send > 1000){

//                 sendMessage("OBSTACLE|STOPPED");
//                 last_obstacle_msg_send = millis(); 
//             }
//             if (1){


//             }
//             break;

//         default:
//             Serial.println("You should never get here in normal operation");
//             break;
//   }


// TODO send back ack
  return current_rover_state;
}



int wifi_state_machine(){
    unsigned long reconnection_time_0;

    switch (wifi_current_state){

        case WIFI_DISCONNECTED:
           wifi_current_state = WIFI_RECONNECTING;
        break;

        case WIFI_RECONNECTING:
            WiFi.begin(WIFI_SSID,WIFI_PSD);
            reconnection_time_0 = millis();
            while(WiFi.status()!=WL_CONNECTED){
                if(millis()-reconnection_time_0 > 5000){
                    Serial.println("Wifi connection timeout");
                    wifi_current_state = WIFI_DISCONNECTED; 
                }
            }
        break;

        case WIFI_CONNECTED:
            if(WiFi.status()!=WL_CONNECTED){
                wifi_current_state = WIFI_DISCONNECTED;
            }
        break;

        default:
        Serial.println("You should never get here in normal operation");
        break;
    }
    return wifi_current_state;
}


int socket_state_machine(){
    static unsigned long lastconnet_time;
    switch (current_socket_state)
    {
    case SOCKET_DISCONNECTED:
        current_socket_state = SOCKET_RECONNECTING;
        reconnecting_timer_0 = millis();
        break;
    case SOCKET_RECONNECTING:
        if(millis()-reconnecting_timer_0 > 5000){
            Serial.println(" Unable to connect to server... Restarting client");
            //ESP.restart();
            current_socket_state = SOCKET_DISCONNECTED;
        }
        if(millis()-lastconnet_time > 1000){
        Serial.println("Reconnecting");
        if (espclient.connect(SERVER,PORT)){
            espclient.printf("ROVER|%d|ON.",ROVER_ID);
            current_socket_state = SOCKET_CONNECTED;

        }
        lastconnet_time = millis();
        }

        break;
    case SOCKET_CONNECTED:
        if(!espclient.connected()){
            current_socket_state = SOCKET_DISCONNECTED;
        }
        break;


    default:
        break;
    }
    return current_socket_state;
}


String getMessage(){
    String buffer = "";
    //Serial.println("here in msg : ");
    ///delay(500);
    if(espclient.available()){
        buffer = espclient.readStringUntil('.');
    }
    return buffer;
}

int sendMessage(String Msg){

    espclient.printf("ROVER|%d|%s.",ROVER_ID,Msg.c_str());
    delay(10);
    return 0;
}
int sendState(int state){
    espclient.printf("ROVER|%d|STATE:%d.",ROVER_ID,state);
    delay(10);
    return 0;
}
