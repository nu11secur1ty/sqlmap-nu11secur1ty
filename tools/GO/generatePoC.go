// @nu11secur1ty 2023
package main

import (
    "fmt"
    "log"
    "os"
)

func main() {
	
    f, err := os.Create("exploit.txt")

    if err != nil {
        log.Fatal(err)
    }
	
    defer f.Close()

    val := `<YOUR_POST_or_GET_Request_from_BurpSuite_here>`

    data := []byte(val)

    _, err2 := f.Write(data)

    if err2 != nil {
        log.Fatal(err2)
    }
		fmt.Println("done..The PoC was created, execute python exploit.py...")
}
