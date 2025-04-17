using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Threading.Tasks;
using UnityEngine.Networking;
using System;

public class DialogueSystem : MonoBehaviour
{
    [Header("UI References")]
    public GameObject dialoguePanel;
    public TMP_Text npcText;
    public TMP_InputField playerInput;
    public Button sendButton;
    
    [Header("API Settings")]
    public string apiEndpoint = "https://project-bloodrain.onrender.com/npc-response";
    public string playerId = "player_123"; // You can generate this dynamically
    
    private void Start()
    {
        dialoguePanel.SetActive(false);
        sendButton.onClick.AddListener(SendPlayerMessage);
    }

    public void StartDialogue()
    {
        dialoguePanel.SetActive(true);
        npcText.text = "Greetings, child. What brings you to the Witches' Forest?";
        playerInput.Select();
    }

    public async void SendPlayerMessage()
    {
        string message = playerInput.text;
        if(string.IsNullOrWhiteSpace(message)) return;
        
        sendButton.interactable = false;
        playerInput.interactable = false;
        
        try
        {
            string jsonPayload = $"{{\"message\":\"{message}\", \"player_id\":\"{playerId}\"}}";
            string npcResponse = await PostToAPI(jsonPayload);
            
            npcText.text = npcResponse;
            playerInput.text = "";
        }
        catch(Exception e)
        {
            npcText.text = "My magic fails me... try again later.";
            Debug.LogError($"API Error: {e.Message}");
        }
        finally
        {
            sendButton.interactable = true;
            playerInput.interactable = true;
            playerInput.Select();
        }
    }

    private async Task<string> PostToAPI(string jsonPayload)
    {
        using(UnityWebRequest webRequest = new UnityWebRequest(apiEndpoint, "POST"))
        {
            byte[] jsonToSend = new System.Text.UTF8Encoding().GetBytes(jsonPayload);
            webRequest.uploadHandler = new UploadHandlerRaw(jsonToSend);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");
            
            var operation = webRequest.SendWebRequest();
            
            while(!operation.isDone)
                await Task.Yield();
            
            if(webRequest.result != UnityWebRequest.Result.Success)
            {
                throw new Exception(webRequest.error);
            }
            
            return JsonUtility.FromJson<APIResponse>(webRequest.downloadHandler.text).reply;
        }
    }

    [System.Serializable]
    private class APIResponse
    {
        public string reply;
    }
}