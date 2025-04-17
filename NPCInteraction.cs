using UnityEngine;
using UnityEngine.Events;

public class NPCInteraction : MonoBehaviour
{
    [Header("Settings")]
    public float interactionRadius = 2f;
    public LayerMask playerLayer;
    
    [Header("Events")]
    public UnityEvent onInteractionStart;
    
    private bool playerInRange = false;
    private GameObject player;

    void Update()
    {
        playerInRange = Physics2D.OverlapCircle(transform.position, interactionRadius, playerLayer);
        
        if(playerInRange && Input.GetKeyDown(KeyCode.E))
        {
            onInteractionStart.Invoke();
        }
    }

    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.yellow;
        Gizmos.DrawWireSphere(transform.position, interactionRadius);
    }
}