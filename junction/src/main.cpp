
#include <Arduino.h>
#include <WiFi.h>
#include "configs.h"

#define WIFI_DISCONNECTED 0
#define WIFI_CONNECTED 1
#define WIFI_RECONNECTING 2

#define SOCKET_DISCONNECTED 0
#define SOCKET_RECONNECTING 1
#define SOCKET_CONNECTED 2

int wifi_current_state = WIFI_DISCONNECTED;
int current_socket_state=SOCKET_DISCONNECTED;
WiFiClient espclient;
int direction;
int current_position;
int required_position;
String incomingMsg,Message;
enum JUNCTIION_STATES_ENUM{
    IDLE,
    ROVER_CROSS,
    ROVER_CROSS_INTER,
    ROVER_CROSS2,
    ROVER_HERE,
    ROTATE,
    ROVER_READY_TO_LEAVE,
    ROVER_LEAVING,
    ROVER_LEAVING2,
    ROVER_LEFT,
    JUNCTION_ERROR
};

String statearray[] = {
    "IDLE",
    "ROVER_CROSS",
    "ROVER_CROSS_INTER",
    "ROVER_CROSS2",
    "ROVER_HERE",
    "ROTATE",
    "ROVER_READY_TO_LEAVE",
    "ROVER_LEAVING",
    "ROVER_LEAVING2",
    "ROVER_LEFT",
    "JUNCTION_ERROR"
};
enum ROTATING_STATES{
    WAIT,
    ENTRY,
    STRAIGHT,
    CROSS,
    ROTATE_CW,
    ROTATE_CCW,
    ROTATING,
    SEND_MESSAGE,
    DONE,
    ERROR_ROTATION
};
String rotating_state_arrray[]={
    "WAIT",
    "ENTRY",
    "STRAIGHT",
    "CROSS",
    "ROTATE_CW",
    "ROTATE_CCW",
    "ROTATING",
    "SEND_MESSAGE",
    "DONE",
    "ERROR_ROTATION"

};





int junctionStateMachine();
int rotating_state_machine();


uint8_t JUNCTION_STATE = IDLE;
uint8_t ROTATING_STATE = WAIT;
int wifi_state_machine();
int socket_state_machine();
String getMessage();
int sendMessage(String);
int sendState(int state);
void turnAllOutputOff();
int wifiprev = WIFI_DISCONNECTED;
int soceketprev = SOCKET_DISCONNECTED;
int junctionprev =IDLE;
int rotateprev = ENTRY;

uint8_t destination = STRAIGHT;

unsigned long last_state_update = 0l;
unsigned long wifi_reconnection_time_0 = 0l;
unsigned long socket_reconnecting_timer_0= 0l;
unsigned long rotation_start_timer_0  = 0l;
unsigned long rover_cross1_timer_0 = 0l;
unsigned long rover_cross2_timer_0 = 0l;


void setup(){

pinMode(SENSOR_A1_PIN,INPUT_PULLDOWN);
pinMode(SENSOR_A2_PIN,INPUT_PULLDOWN);
pinMode(IR_SENSOR_PIN,INPUT_PULLDOWN);
pinMode(BUZZER_PIN,OUTPUT);
pinMode(TURN_CCW_PIN,OUTPUT);
pinMode(TURN_CW_PIN,OUTPUT);

    Serial.begin(115200);
}

void loop(){
    if(wifiprev!=wifi_current_state||soceketprev!=current_socket_state||junctionprev!=JUNCTION_STATE||millis()-last_state_update>2000){
        Serial.printf("wifi:%d|socket:%d|client:%d::%s::%s \n",wifi_current_state,current_socket_state,JUNCTION_STATE,statearray[JUNCTION_STATE].c_str(),rotating_state_arrray[ROTATING_STATE].c_str());
        wifiprev = wifi_current_state;
        soceketprev = current_socket_state;
        junctionprev = JUNCTION_STATE;
        rotateprev  =ROTATING_STATE;
    }


    if(junctionprev!=JUNCTION_STATE || millis()-last_state_update>2000){
        sendState(JUNCTION_STATE);
        last_state_update = millis();
    }
    if(wifi_state_machine()==WIFI_CONNECTED){
        if(socket_state_machine()==SOCKET_CONNECTED){
            junctionStateMachine();
            rotating_state_machine();
        }
    }

}
int junctionStateMachine(){
    int IR_Sensor = digitalRead(IR_SENSOR_PIN);
    //int A1 = digitalRead(SENSOR_A1_PIN);
    //int A2 = digitalRead(SENSOR_A2_PIN);
    incomingMsg = getMessage();
    if (incomingMsg.length() > 0){
        Message = incomingMsg;
    }

    switch(JUNCTION_STATE){


        case IDLE:
            if (IR_Sensor == HIGH){
            rover_cross1_timer_0 = millis();
            sendMessage("SLOWDOWN");
            JUNCTION_STATE = ROVER_CROSS;
            }
            break;
        case ROVER_CROSS:
            if (millis()- rover_cross1_timer_0 > 300){

                if(IR_Sensor == LOW){
                    JUNCTION_STATE = ROVER_CROSS_INTER;
                }
            }
            break;
        case ROVER_CROSS_INTER:
            if (IR_Sensor == HIGH){
                sendMessage("STOP");
                JUNCTION_STATE = ROVER_CROSS2;
                rover_cross2_timer_0 = millis();
            }
            break;
        case ROVER_CROSS2:
            if(millis() - rover_cross2_timer_0 > 500){
                if (IR_Sensor ==HIGH){
                    JUNCTION_STATE = ROVER_HERE;
                }
            }
            break;
        case ROVER_HERE:
            if(Message.compareTo("ROTATE|STRAIGHT") == 0){
                destination = STRAIGHT;
                Serial.println("rotate Straight");
                ROTATING_STATE = ENTRY;
                JUNCTION_STATE = ROTATE;
            }
            if (Message.compareTo("ROTATE|CROSS") == 0){
                destination = CROSS;
                Serial.println("rotate cross");
                ROTATING_STATE = ENTRY;
                JUNCTION_STATE = ROTATE;
            }
            break;
        case ROTATE:
            //Serial.print(".");
            delay(10);
            if(ROTATING_STATE == DONE){
                ROTATING_STATE = WAIT; 
                JUNCTION_STATE = ROVER_READY_TO_LEAVE;
                Message = String("");
                break;
            }
            if(ROTATING_STATE == ERROR_ROTATION){
                JUNCTION_STATE = JUNCTION_ERROR;
            }
            break;
        case ROVER_READY_TO_LEAVE:
            if(IR_Sensor == LOW){
                JUNCTION_STATE = ROVER_LEAVING;
                rover_cross1_timer_0 = millis();
            }
            break;
        case ROVER_LEAVING:
            if((millis() - rover_cross1_timer_0) > 500){
                if(IR_Sensor == HIGH){
                    JUNCTION_STATE = ROVER_LEAVING2;

                }
            }
            break;
        case ROVER_LEAVING2:
            if((millis()-rover_cross2_timer_0)> 500)
                if(IR_Sensor == LOW){
                    JUNCTION_STATE = ROVER_LEFT;
                }
            break;
        case ROVER_LEFT:
            delay(1000);
            JUNCTION_STATE = IDLE;
            break;
        case JUNCTION_ERROR:
            turnAllOutputOff();
            break;
    }
    return JUNCTION_STATE;
}

int rotating_state_machine(){

int sensor_A1 = digitalRead(SENSOR_A1_PIN);
int sensor_A2 = digitalRead(SENSOR_A2_PIN);
//int IR_Sensor = digitalRead(IR_SENSOR_PIN);


switch (ROTATING_STATE){

    case  ENTRY:
        Serial.println(sensor_A1);
        Serial.println(sensor_A2);
        if (sensor_A1==HIGH && sensor_A2 ==HIGH){
            ROTATING_STATE = STRAIGHT;
        }
        if ((sensor_A1 == HIGH && sensor_A2 == LOW) || (sensor_A1 == LOW && sensor_A2 == HIGH )){
            ROTATING_STATE = CROSS;
        }
        if (sensor_A1 == LOW && sensor_A2 ==LOW){
            ROTATING_STATE = ROTATE_CW;
        }

        break;

    case  STRAIGHT:
        turnAllOutputOff();
        current_position = STRAIGHT;
        if (destination == current_position){
            ROTATING_STATE = SEND_MESSAGE;
        break;
        }
        ROTATING_STATE = ROTATE_CW;
        break;

    case  CROSS:
        current_position = CROSS;
        turnAllOutputOff();
        if (destination == current_position){
            ROTATING_STATE = SEND_MESSAGE;

        break;
        }
        ROTATING_STATE = ROTATE_CCW;
        break;

    case  ROTATE_CW:
        digitalWrite(TURN_CW_PIN,HIGH);
        digitalWrite(TURN_CCW_PIN,LOW);
        rotation_start_timer_0 = millis();
        ROTATING_STATE = ROTATING;
        break;

    case  ROTATE_CCW:
        digitalWrite(TURN_CCW_PIN,HIGH);
        digitalWrite(TURN_CW_PIN,LOW);
        rotation_start_timer_0 = millis();
        ROTATING_STATE = ROTATING;
        break;

    case  ROTATING:
        if (millis() - rotation_start_timer_0 > TIME_BUZZER){
            digitalWrite(BUZZER_PIN,HIGH);
        }
        if (millis() - rotation_start_timer_0 > 30000){
            Serial.println("Rotating for too long going to error state");
            ROTATING_STATE = ERROR_ROTATION;
        }
        if (sensor_A1==HIGH && sensor_A2 ==HIGH){
            ROTATING_STATE = STRAIGHT;
        }
        if ((sensor_A1 == HIGH && sensor_A2 == LOW) || (sensor_A1 == LOW && sensor_A2 == HIGH )){
            ROTATING_STATE = CROSS;
        }
        break;

    case SEND_MESSAGE:
        sendMessage("Rotation done");
        ROTATING_STATE = DONE;
        break;

    case DONE:

        break;

    case ERROR_ROTATION:

        break;
}

return ROTATING_STATE;
}

int wifi_state_machine(){

    switch (wifi_current_state){

        case WIFI_DISCONNECTED:
           wifi_reconnection_time_0 = millis();
           wifi_current_state = WIFI_RECONNECTING;
        break;

        case WIFI_RECONNECTING:
            WiFi.begin(WIFI_SSID,WIFI_PSD);
            while(WiFi.status()!=WL_CONNECTED){
                if(millis()-wifi_reconnection_time_0 > 5000){
                    Serial.println("Wifi connection timeout");
                    wifi_current_state = WIFI_DISCONNECTED;
                    wifi_reconnection_time_0 = millis();
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
        socket_reconnecting_timer_0 = millis();
        break;
    case SOCKET_RECONNECTING:
        if(millis()-socket_reconnecting_timer_0 > 5000){
            Serial.println(" Unable to connect to server... Restarting client");
            //ESP.restart();
            current_socket_state = SOCKET_DISCONNECTED;
        }
        if(millis()-lastconnet_time > 1000){
        Serial.println("Reconnecting");
        if (espclient.connect(SERVER,PORT)){
            espclient.printf("JUNCTION|ON.");
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

    espclient.printf("JUNCTION|%d|%s.",ID,Msg.c_str());
    delay(10);
    return 0;
}
int sendState(int state){
    espclient.printf("JUNCTION|%d|STATE:%d.",ID,state);
    delay(10);
    return 0;
}

void turnAllOutputOff(){

    digitalWrite(BUZZER_PIN,LOW);
    digitalWrite(TURN_CW_PIN,LOW);
    digitalWrite(TURN_CCW_PIN,LOW);

}
