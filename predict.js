/*
import "@ui5/webcomponents/dist/Button";
import "@ui5/webcomponents/dist/TextArea";
import "@ui5/webcomponents/dist/DatePicker";
import "@ui5/webcomponents/dist/Table.js";
import "@ui5/webcomponents/dist/TableColumn.js";
import "@ui5/webcomponents/dist/TableRow.js";
import "@ui5/webcomponents/dist/TableCell.js";
*/

// after DOM contents are loaded
window.addEventListener( "DOMContentLoaded", function() {
  // setup 

  // Reqeust prediction
  const execPredict = async ( event ) => {
    let modalProgress = document.getElementById( "progress-modal" );
    let progressCaption = document.getElementById( "progress-caption" );
    progressCaption.innerHTML = "予測の実行準備をしています";
 
    modalProgress.classList.toggle( "is-active" );
 　 
    let predictResult = null;

    try {
      let source = document.getElementById( "dataText" );    

      const fetch_predict_res = await fetch("/predict", {
        method: "POST",
        headers: { "Accept": "application/json", "Content-Type": "application/json"},
        body: JSON.stringify({"type": "predict",
                              "data": source.value})
      });
      const result_predict_json = await fetch_predict_res.json();
      if( !fetch_predict_res.ok ) {
        progressCaption.innerHTML = "予測実行のリクエストに失敗しました。";
          throw new Error("Failed to get predict response.");        
      }

      if(result_predict_json["status"] == "error"){ //WEBAPI側で"error"と判断されたらアラートする
         progressCaption.innerHTML = "予測実行のリクエストに失敗しました。";
            throw new Error("Failed to get predict response.");        
      }

      const predict_request_id = result_predict_json['requestid']; 
      let resultparams = new URLSearchParams();
      resultparams.set("type", "result");
      resultparams.set("requestid", predict_request_id);
      for (let i = 0;  i < 30;  i++) {
        const echo_res = await fetch("/result" + '?' + resultparams.toString());
        const result_result = await echo_res.json();
        if ( "result" in result_result && 
             "status" in result_result &&
             result_result["status"] == "success") {
          predictResult = result_result['result']
          break;
        }
        await new Promise(r => setTimeout(r,1500));
      }
        
      if ( predictResult == null ) {
           progressCaption.innerHTML = "予測実行の取得に失敗しました。";
           predictResult = "実行失敗";
           await new Promise(r => setTimeout(r,2000));
      } else {
        progressCaption.innerHTML = "予測が完了しました。";
        await new Promise(r => setTimeout(r,1000));          
      }


    } catch (e) {
      progressCaption.innerHTML = "予測実行サーバーの呼び出しに失敗しました。";
      await new Promise(r => setTimeout(r,2000));
    }

    modalProgress.classList.toggle( "is-active" );

    let target = document.getElementById( "resultText" );
    target.value = predictResult;
  };
  let btnExecPredict = document.getElementById( "execPredict" );
  btnExecPredict.addEventListener( "click", execPredict );

  (async() => {
    const default_data_res = await fetch("/default_data");
    const default_data_text = await default_data_res.text();
    let target = document.getElementById( "dataText" );
    target.value = default_data_text;
  })();

});