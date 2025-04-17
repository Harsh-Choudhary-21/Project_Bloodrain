using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;

public class NPCChatManager : MonoBehaviour
{
    public InputField playerInputField;
    public Text npcResponseText;
    private string apiURL = "https://your-ngrok-url.ngrok.io/npc-response";  // Replace with your real endpoint

    [System.Serializable]
    class PlayerInput
    {
        public string player_id;
        public string player_input;
    }

    [System.Serializable]
    class NPCResponse
    {
        public string npc_response;
    }

    public void OnSendButtonClick()
    {
        string message = playerInputField.text;
        if (!string.IsNullOrEmpty(message))
        {
            StartCoroutine(SendMessageToAPI(message));
        }
    }

    IEnumerator SendMessageToAPI(string message)
    {
        PlayerInput input = new PlayerInput { player_id = "player_001", player_input = message };
        string json = JsonUtility.ToJson(input);

        UnityWebRequest request = new UnityWebRequest(apiURL, "POST");
        byte[] body = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(body);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            NPCResponse result = JsonUtility.FromJson<NPCResponse>(request.downloadHandler.text);
            npcResponseText.text = result.npc_response;
        }
        else
        {
            npcResponseText.text = "Error communicating with Serath.";
        }
    }
}
