FIRST TO RUN IT MAKE A enviro.env file for GROQ_API=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

APPROACH

1.   In this you first upload the document and it is readed through API of Groq .We use Groq API as its is freely available .
2.   After upload you have variuos option ex find summary of the document , challenge me, ask ask question .

3.   If you are asking question then it will give answer which the groq have readed ,
4.   If you challenge there is prompt for challenge in which it ask three question and you have to give answer . And result is shown on different endpoint as it check whether it contains keywords present in the document and based on it .It will give the result.

5.   To run it first write pip intall -r requirements.txt

6.   python app.py as I have used flask for backend

