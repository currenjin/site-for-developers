package com.rivercory.sitefordevelopers

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout


class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        var myWeb = findViewById<WebView>(R.id.webview)
        var layoutswiperefresh = findViewById<SwipeRefreshLayout>(R.id.layout_swipe_refresh)

        myWeb.webViewClient = WebViewClient()
        myWeb.getSettings().setSupportZoom(true);
        myWeb.getSettings().setJavaScriptEnabled(true);
        myWeb.settings.javaScriptCanOpenWindowsAutomatically = true;
        myWeb.settings.domStorageEnabled = true;
        myWeb.getSettings().setLoadsImagesAutomatically(true);
        myWeb.getSettings().setBuiltInZoomControls(false);
        myWeb.getSettings().setCacheMode(WebSettings.LOAD_DEFAULT);

        myWeb.apply {
            loadUrl("https://site-for-developers.vercel.app")
            settings.javaScriptEnabled = true
        }

        layoutswiperefresh.setColorSchemeResources(
            R.color.primary_500
        );

        layoutswiperefresh.setOnRefreshListener(SwipeRefreshLayout.OnRefreshListener {
            myWeb.reload()
            layoutswiperefresh.setRefreshing(false)
        })
    }
}