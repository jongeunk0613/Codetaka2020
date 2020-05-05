package Graph_07;

import java.util.*;
 
 

public class BfsTest02 {
    
    static int[][] ad;
    static boolean[] visit;
    static int Ne, Nv;
    
    public static void bfs(int i){
        Queue <Integer> q = new <Integer> LinkedList();
        
        q.offer(i);
        visit[i] = true;
        
        while(!q.isEmpty()){
            int temp = q.poll();
            System.out.print(temp);
            
            for(int j = 1; j <= Nv; j++){
                if(ad[temp][j] == 1 && visit[j] == false){
                    q.offer(j);
                    visit[j] = true;                   // 큐에 넣을 노드들을 잠재적으로 방문한다는 가정하에 입력
                    }
                }
            
            }    
    }
    
    public static void main(String[] args){
        Scanner scan = new Scanner(System.in);
        Nv = scan.nextInt();
        Ne = scan.nextInt();
        ad = new int[Nv+1][Nv+1];
        visit = new boolean[Nv+1];
        
        for(int i = 0; i < Ne; i++){
            int t1, t2;
            t1 = scan.nextInt();
            t2 = scan.nextInt();
            
            ad[t1][t2] = ad[t2][t1] = 1;
        }
        
        bfs(1);
        
    }
    
}
