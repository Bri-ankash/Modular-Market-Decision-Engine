//+------------------------------------------------------------------+
//|                                           MMDE_Broadcaster.mq5   |
//|                                  Copyright 2026, MMDE_Engine     |
//|                                             https://mmde.com     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, MMDE_Engine"
#property link      "https://mmde.com"
#property version   "1.00"
#property strict

//--- input parameters
input string   InpSecret   = "YOUR_SECRET_HERE"; // Your MMDE Webhook Secret
input string   InpURL      = "https://modular-market-decision-engine.onrender.com/api/mmde/tv-webhook"; // Your Webhook URL
input int      InpCandles  = 20; // Number of candles to send

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("MMDE Broadcaster Started. Secret: ", InpSecret);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   static datetime last_time = 0;
   datetime current_time = iTime(_Symbol, _Period, 0);

   if(current_time != last_time)
   {
      last_time = current_time;
      BroadcastCandles();
   }
}

//+------------------------------------------------------------------+
//| Send data to MMDE                                                |
//+------------------------------------------------------------------+
void BroadcastCandles()
{
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 1, InpCandles, rates);
   
   if(copied <= 0) return;

   string candles_json = "[";
   for(int i=copied-1; i>=0; i--)
   {
      string c = "{\"o\":" + DoubleToString(rates[i].open, _Digits) + 
                 ",\"h\":" + DoubleToString(rates[i].high, _Digits) + 
                 ",\"l\":" + DoubleToString(rates[i].low, _Digits) + 
                 ",\"c\":" + DoubleToString(rates[i].close, _Digits) + 
                 ",\"v\":" + IntegerToString(rates[i].tick_volume) + 
                 ",\"t\":\"" + TimeToString(rates[i].time) + "\"}";
      candles_json += c;
      if(i > 0) candles_json += ",";
   }
   candles_json += "]";

   string payload = "{\"secret\":\"" + InpSecret + "\",\"symbol\":\"" + _Symbol + "\",\"interval\":\"" + EnumToString(_Period) + "\",\"market\":\"forex\",\"candles\":" + candles_json + "}";
   
   char data[];
   char result[];
   string result_headers;
   StringToCharArray(payload, data, 0, WHOLE_ARRAY, CP_UTF8);
   
   int res = WebRequest("POST", InpURL, "Content-Type: application/json\r\n", 5000, data, result, result_headers);
   
   if(res == 200)
      Print("✅ MMDE: Candles broadcasted successfully for ", _Symbol);
   else
      Print("❌ MMDE: Failed to broadcast. Error: ", res);
}
//+------------------------------------------------------------------+
