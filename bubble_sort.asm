.data

arr: .word 23, 64,12, 15, 89,73, 32,55,76,53


.text

main:
    
    la $t0,arr
    
    addi $t2, $t0,36 #j = a+36

    loop1:
        addi $t1, $t0, 0

        loop2:
            ld $t3, 0($t1) 
            ld $t4, 4($t1)
            slt $t5, $t3, $t4
           bne $t5, $zero, inc
                st $t3, 4($t1) 
                st $t4, 0($t1)
            inc:
            addi $t1, $t1, 4
            bne $t1, $t2, loop2

            addi $t2, $t2, -4
        bne $t2, $t0, loop1
