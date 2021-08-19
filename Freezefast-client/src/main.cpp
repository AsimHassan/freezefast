#include <Arduino.h>
#include <WiFi.h>
#include <configs.h>


enum STATION_STATES {
STOPPED,
RESET,
CALL,
WAITFORCALLACK,
CALLED,
ROVER_CROSSED,
ROVER_CROSSED_AGAIN ,
ROVER_REACHED,
GO_PRESSED,
GONE,
EMERGENCY,
IR_LOW,
ROVERCROSS_INTER,
ROVER_LEAVING,
ROVER_LEAVING_INTER,
ROVER_LEAVING_2
};

String STATE_ARRAY[] ={
"STOPPED",
"RESET",
"CALL",
"WAITFORCALLACK",
"CALLED",
"ROVER_CROSSED",
"ROVER_CROSSED_AGAIN" ,
"ROVER_REACHED",
"GO_PRESSED",
"GONE",
"EMERGENCY",
"IR_LOW",
"ROVERCROSS_INTER",
"ROVER_LEAVING",
"ROVER_LEAVING_INTER",
"ROVER_LEAVING_2"
};

#define WIFI_DISCONNECTED 0
#define WIFI_CONNECTED 1
#define WIFI_RECONNECTING 2

#define SOCKET_DISCONNECTED 0
#define SOCKET_RECONNECTING 1
#define SOCKET_CONNECTED 2

int previous_state_station = RESET;
int current_state_station = RESET;
uint8_t prev_state_for_emergency = RESET;
int wifi_current_state = WIFI_DISCONNECTED;
int current_socket_state=SOCKET_DISCONNECTED;

bool rover_owner = true;
bool green_led_status =LOW;
bool emergency_ack_flag = false;
unsigned long server_ack_timer_0;
unsigned long server_ack_timer_now;
unsigned long green_led_time_last_toggle;
unsigned long reconnecting_timer_0;
unsigned long reconnection_time_0;
unsigned long emergency_timer_0;
unsigned long last_state_update = 0;
unsigned long rovercrossing_0;
unsigned long roverhere_0;
WiFiClient espclient;


int wifiprev = WIFI_DISCONNECTED;
int soceketprev = SOCKET_DISCONNECTED;
int clientprev =RESET;

int socket_state_machine();
int wifi_state_machine();
int station_state_machine();
String getMessage();
int sendMessage(String);
int sendState(int state);

void setup(){

    pinMode(GREEN_LED_PIN,OUTPUT);
    pinMode(RED_LED_PIN,OUTPUT);
    digitalWrite(RED_LED_PIN,LOW);
    digitalWrite(GREEN_LED_PIN,LOW);
    pinMode(GREEN_SWITCH_PIN,INPUT_PULLDOWN);
    pinMode(RED_SWITCH_PIN,INPUT_PULLDOWN);
    pinMode(IR_RECEIVER_PIN,INPUT_PULLDOWN);

    Serial.begin(115200);
    WiFi.begin(WIFI_SSID,WIFI_PSD);
    while (WiFi.status()!= WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Wifi Connected");
    wifi_current_state = WIFI_CONNECTED;

}
void loop(){
    if(clientprev!=current_state_station || millis()-last_state_update>2000){
        sendState(current_state_station);
        last_state_update = millis();
    }
    if(wifiprev!=wifi_current_state||soceketprev!=current_socket_state||clientprev!=current_state_station){
        Serial.printf("wifi:%d|socket:%d|STATION_STATE:%s \n",wifi_current_state,current_socket_state,STATE_ARRAY[current_state_station].c_str());
        wifiprev = wifi_current_state;
        soceketprev = current_socket_state;
        clientprev = current_state_station;
    }

    if(wifi_state_machine()==WIFI_CONNECTED){
        if(socket_state_machine()==SOCKET_CONNECTED){
            station_state_machine();
        }
    }

}



int station_state_machine(){


    String msgIn = getMessage();
    int msglength = msgIn.length();
    if(msglength!=0){
        Serial.println(msgIn);
    }
    int greenswitch = digitalRead(GREEN_SWITCH_PIN);
    int redswitch = digitalRead(RED_SWITCH_PIN);
    int roverIR = digitalRead(IR_RECEIVER_PIN);
    if(redswitch==HIGH){
        previous_state_station = current_state_station;
        current_state_station = EMERGENCY;
    }


    switch (current_state_station){
        case RESET:{
            digitalWrite(RED_LED_PIN,LOW);
            digitalWrite(GREEN_LED_PIN,LOW);

           if(roverIR == LOW){
                previous_state_station = current_state_station;
                current_state_station = IR_LOW;
                return 0;
            }
            if(greenswitch == HIGH){
                previous_state_station = current_state_station;
                current_state_station = CALL;
            }
            break;
        }

        case CALL:
            server_ack_timer_0 = millis();
            Serial.println("sending call");
            sendMessage("CALL");
            previous_state_station = current_state_station;
            current_state_station = WAITFORCALLACK;
            break;

        case WAITFORCALLACK:
            server_ack_timer_now = millis();
            if(server_ack_timer_now - server_ack_timer_0 > 5000){
                previous_state_station = current_state_station;
                current_state_station = RESET;
                return current_state_station;
            }

            if(msgIn.compareTo("CALL|ACK")==0){
                previous_state_station = current_state_station;
                current_state_station = CALLED;
            }
            break;


        case CALLED:{
            if(millis()-green_led_time_last_toggle> LED_BLINK_DELAY){
                green_led_status = !green_led_status;
                digitalWrite(GREEN_LED_PIN,green_led_status);
                green_led_time_last_toggle = millis();
            }
            if(roverIR == LOW){
                previous_state_station = current_state_station;
                current_state_station = IR_LOW; 
                return current_state_station;
            }

            break;
        }
        case IR_LOW:
                sendMessage("ROVERCROSSED");
                current_state_station = ROVER_CROSSED;
            break;

        case ROVER_CROSSED:
            if (msgIn.compareTo("CROSS|NO") == 0){
                rover_owner = false;
                current_state_station = previous_state_station;
                break;

            }
            if (msgIn.compareTo("CROSS|YES") == 0){
                rover_owner = true;
            }
            
            if (roverIR == HIGH){
                current_state_station = ROVERCROSS_INTER;
            }

            break;


        case ROVERCROSS_INTER:
            if (roverIR == LOW){
                sendMessage("STOP");
                current_state_station = ROVER_CROSSED_AGAIN;
                roverhere_0 = millis();
            }
            if (msgIn.compareTo("CROSS|NO") == 0){
                rover_owner = false;
                current_state_station = previous_state_station;

                break;
            }


            break;

        case ROVER_CROSSED_AGAIN:
            if (roverIR == LOW && (millis() - roverhere_0 > 500)){
                current_state_station = ROVER_REACHED;
            }
            break;
        
        case ROVER_REACHED:
            digitalWrite(GREEN_LED_PIN,HIGH);
            if (greenswitch == HIGH){
                current_state_station = GO_PRESSED;
                
                sendMessage("GO");
            } 
            break;

        case GO_PRESSED:
            if (msgIn.compareTo("GO|ACK") == 0){
                current_state_station = ROVER_LEAVING;
                digitalWrite(GREEN_LED_PIN,LOW);
            }
            break;
        
        case ROVER_LEAVING:
            if (roverIR  == HIGH){
                current_state_station = ROVER_LEAVING_INTER;
            }
            break;
        
        case ROVER_LEAVING_INTER:
            if (roverIR == LOW){
                current_state_station = ROVER_LEAVING_2;
                roverhere_0 = millis();
            
            }

            break;
        
        case ROVER_LEAVING_2:
            if (roverIR == HIGH && (millis() - roverhere_0 > 500)){
                current_state_station = GONE;
            }
            break;


        case GONE:
            current_state_station = RESET;
            break;
         
        
        

        case EMERGENCY:{
            if (redswitch == LOW){
            delay(60);
            sendMessage("EMERGENCY");
            emergency_timer_0 = millis();
            current_state_station = STOPPED;
            break;
            }
        }
        case STOPPED:{
            if(msgIn.compareTo("EMERGENCY|ACK")==0){
                digitalWrite(RED_LED_PIN,HIGH);
                emergency_ack_flag = true;

            }
            if(millis()-emergency_timer_0 > 1000 && emergency_ack_flag == false){
                current_state_station = EMERGENCY;
            }

            if(msgIn.compareTo("EMERGENCY|OVER")== 0){

                current_state_station = RESET;
                emergency_ack_flag = false;
            }
           
            break;
        }
    }
    return current_state_station;
}


int wifi_state_machine(){

    switch (wifi_current_state){

        case WIFI_DISCONNECTED:
           reconnection_time_0 = millis();
           wifi_current_state = WIFI_RECONNECTING;
        break;

        case WIFI_RECONNECTING:
            WiFi.begin(WIFI_SSID,WIFI_PSD);
            while(WiFi.status()!=WL_CONNECTED){
                if(millis()-reconnection_time_0 > 5000){
                    Serial.println("Wifi connection timeout");
                    wifi_current_state = WIFI_DISCONNECTED;
                    reconnection_time_0 = millis();
                }
            }
            wifi_current_state = WIFI_CONNECTED;
        break;

        case WIFI_CONNECTED:
            if(WiFi.status()!=WL_CONNECTED){
                wifi_current_state = WIFI_DISCONNECTED;
            }
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
            espclient.printf("STATION|%d|ON.",STATION_ID);
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
    if(espclient.available()){
        buffer = espclient.readStringUntil('.');
    }
    return buffer;
}

int sendMessage(String Msg){

    espclient.printf("STATION|%d|%s.",STATION_ID,Msg.c_str());
    delay(10);
    return 0;
}

int sendState(int state){
    espclient.printf("STATION|%d|STATE:%d.",STATION_ID,state);
    delay(10);
    return 0;
}
