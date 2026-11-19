public class Solution {
    public long PickGifts(int[] gifts, int k) {
        //Job must be done K number of times
        int y = k;
        while(y != 0){
            //First task is to denote largest pile of gifts
            //Initialize integers used for the largest and the address of the largest
            int largest = 0;
            int largestAddress = 0;
            for(int x = 0; x < gifts.Length; x++){
                if(largest < gifts[x]){
                    largest = gifts[x];
                    largestAddress = x;
                }
            }
            //Get floor of the square root of the highest value
            if( (int) Math.Floor(Math.Sqrt(largest)) <= 0){
                largest = 1;
            }
            gifts[largestAddress] = (int) Math.Floor(Math.Sqrt(largest));
            y--;
            //Console.WriteLine(largest);
        }
        //Return number of gifts after k
        long giftNum = 0;
        for(int x = 0; x < gifts.Length; x++){
            giftNum += gifts[x];
        }
        return(giftNum);
    }
}
