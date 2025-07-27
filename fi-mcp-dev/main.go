package main

import (
    "context"
    "fmt"
    "html/template"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/epifi/fi-mcp-lite/middlewares"
    "github.com/epifi/fi-mcp-lite/pkg"
)

var (
    authMW        = middlewares.NewAuthMiddleware()
    googleAPIKey  string
)

func main() {

    mux := http.NewServeMux()

    // ————— Login UI —————
    mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))
    mux.HandleFunc("/mockWebPage", webPageHandler)
    mux.HandleFunc("/login", loginHandler)

    // ————— Polling JSON endpoints —————
    mux.Handle("/api/net_worth", withAuth(apiHandler("fetch_net_worth.json")))
    mux.Handle("/api/credit_report", withAuth(apiHandler("fetch_credit_report.json")))
    mux.Handle("/api/epf_details", withAuth(apiHandler("fetch_epf_details.json")))
    mux.Handle("/api/mf_transactions", withAuth(apiHandler("fetch_mf_transactions.json")))
    mux.Handle("/api/bank_transactions", withAuth(apiHandler("fetch_bank_transactions.json")))
    mux.Handle("/api/stock_transactions", withAuth(apiHandler("fetch_stock_transactions.json")))


    // ————— SSE streaming endpoints —————
    mux.Handle("/stream/net_worth", withAuth(sseStream("fetch_net_worth.json", 2*time.Second)))
    mux.Handle("/stream/credit_report", withAuth(sseStream("fetch_credit_report.json", 5*time.Second)))
    mux.Handle("/stream/epf_details", withAuth(sseStream("fetch_epf_details.json", 2*time.Second)))
    mux.Handle("/stream/mf_transactions", withAuth(sseStream("fetch_mf_transactions.json", 2*time.Second)))
    mux.Handle("/stream/bank_transactions", withAuth(sseStream("fetch_bank_transactions.json", 2*time.Second)))
    mux.Handle("/stream/stock_transactions", withAuth(sseStream("fetch_stock_transactions.json", 2*time.Second)))
    

    port := pkg.GetPort()
    log.Printf("Listening on :%s\n", port)
    log.Fatal(http.ListenAndServe(":"+port, mux))
}

// ————— auth wrapper —————
func withAuth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        c, err := r.Cookie("sessionid")
        if err != nil {
            http.Error(w, "login required", http.StatusUnauthorized)
            return
        }
        phone := authMW.GetPhoneNumber(c.Value)
        if phone == "" {
            http.Error(w, "login required", http.StatusUnauthorized)
            return
        }
        ctx := context.WithValue(r.Context(), "phone", phone)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// ————— generic JSON file server —————
func apiHandler(fileName string) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        phone := r.Context().Value("phone").(string)
        data, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/%s", phone, fileName))
        if err != nil {
            http.Error(w, "data not found", http.StatusInternalServerError)
            return
        }
        w.Header().Set("Content-Type", "application/json")
        w.Write(data)
    })
}

// ————— SSE helper —————
func sseStream(fileName string, interval time.Duration) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        phone := r.Context().Value("phone").(string)
        w.Header().Set("Content-Type", "text/event-stream")
        w.Header().Set("Cache-Control", "no-cache")
        w.Header().Set("Connection", "keep-alive")

        fl, ok := w.(http.Flusher)
        if !ok {
            http.Error(w, "streaming unsupported", http.StatusInternalServerError)
            return
        }
        ticker := time.NewTicker(interval)
        defer ticker.Stop()

        for {
            select {
            case <-r.Context().Done():
                return
            case <-ticker.C:
                data, err := os.ReadFile(fmt.Sprintf("test_data_dir/%s/%s", phone, fileName))
                if err != nil {
                    log.Println("read error:", err)
                    continue
                }
                fmt.Fprintf(w, "data: %s\n\n", data)
                fl.Flush()
            }
        }
    })
}

// ————— Login UI handlers (unchanged) —————
func webPageHandler(w http.ResponseWriter, r *http.Request) {
    sid := r.URL.Query().Get("sessionId")
    if sid == "" {
        http.Error(w, "sessionId is required", http.StatusBadRequest)
        return
    }
    tmpl, _ := template.ParseFiles("static/login.html")
    data := struct {
        SessionId string
        Allowed   []string
    }{sid, pkg.GetAllowedMobileNumbers()}
    tmpl.Execute(w, data)
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    sid := r.FormValue("sessionId")
    ph := r.FormValue("phoneNumber")
    if sid == "" || ph == "" {
        http.Error(w, "sessionId & phoneNumber required", http.StatusBadRequest)
        return
    }
    authMW.AddSession(sid, ph)
    http.SetCookie(w, &http.Cookie{Name: "sessionid", Value: sid, Path: "/"})
    tmpl, _ := template.ParseFiles("static/login_successful.html")
    tmpl.Execute(w, nil)
}
