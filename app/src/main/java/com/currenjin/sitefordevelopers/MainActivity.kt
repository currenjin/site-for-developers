package com.currenjin.sitefordevelopers

import android.os.Bundle
import android.view.KeyEvent
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout

class MainActivity : AppCompatActivity() {
    private lateinit var myWeb: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        myWeb = findViewById(R.id.webview)
        val layoutSwipeRefresh = findViewById<SwipeRefreshLayout>(R.id.layout_swipe_refresh)

        myWeb.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                return false
            }
        }

        myWeb.settings.apply {
            javaScriptEnabled = true
            javaScriptCanOpenWindowsAutomatically = true
            domStorageEnabled = true
            loadsImagesAutomatically = true
            builtInZoomControls = false
            cacheMode = WebSettings.LOAD_DEFAULT
            setSupportZoom(true)
        }

        myWeb.loadUrl("https://sfd.kro.kr")

        layoutSwipeRefresh.setColorSchemeResources(R.color.primary)

        layoutSwipeRefresh.setOnRefreshListener {
            myWeb.reload()
            layoutSwipeRefresh.isRefreshing = false
        }
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        return if (keyCode == KeyEvent.KEYCODE_BACK && myWeb.canGoBack()) {
            myWeb.goBack()
            true
        } else {
            super.onKeyDown(keyCode, event)
        }
    }
}
