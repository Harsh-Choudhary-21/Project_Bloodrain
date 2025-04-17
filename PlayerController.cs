using UnityEngine;

[RequireComponent(typeof(Rigidbody2D))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement Settings")]
    public float moveSpeed = 5f;
    public float acceleration = 10f;
    public float deceleration = 10f;
    
    private Rigidbody2D rb;
    private Vector2 movementInput;
    private Vector2 currentVelocity;

    void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
        rb.gravityScale = 0; // Ensure no gravity affects 2D movement
    }

    void Update()
    {
        // Get raw input for snappier movement
        movementInput = new Vector2(
            Input.GetAxisRaw("Horizontal"),
            Input.GetAxisRaw("Vertical")
        ).normalized;
    }

    void FixedUpdate()
    {
        MovePlayer();
    }

    private void MovePlayer()
    {
        // Calculate target velocity
        Vector2 targetVelocity = movementInput * moveSpeed;
        
        // Smoothly interpolate to target velocity
        rb.velocity = Vector2.SmoothDamp(
            rb.velocity,
            targetVelocity,
            ref currentVelocity,
            targetVelocity.magnitude > 0.1f ? (1f / acceleration) : (1f / deceleration)
        );
    }

    // For debugging
    void OnGUI()
    {
        GUILayout.Label($"Movement Input: {movementInput}");
        GUILayout.Label($"Current Velocity: {rb.velocity}");
    }
}
